"""
File Upload/Download/Delete Views
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import FileResponse, Http404
from django.core.files.base import ContentFile
from groups.models import FileGroup
from .models import EncryptedFile, FileEncryptionKey
from .forms import FileUploadForm
from .encryption import HybridEncryption, encode_for_db, decode_from_db
import os


@login_required
def upload_file(request, group_id):
    """
    Upload and encrypt file for a group
    
    Process:
    1. User uploads file
    2. Generate random AES key
    3. Encrypt file with AES-GCM
    4. For each group member:
       - Encrypt AES key with their RSA public key
       - Store in FileEncryptionKey table
    5. Save encrypted file to disk
    """
    group = get_object_or_404(FileGroup, pk=group_id)
    
    # Check if user is member of group
    if not group.is_member(request.user):
        messages.error(request, 'You are not a member of this group.')
        return redirect('groups:list')
    
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['file']
            
            try:
                # Read file data
                file_data = uploaded_file.read()
                
                # Generate random AES key
                aes_key = HybridEncryption.generate_aes_key()
                
                # Encrypt file with AES-GCM
                encrypted_data = HybridEncryption.encrypt_file_aes(file_data, aes_key)
                
                # Create encrypted file record
                encrypted_file = EncryptedFile.objects.create(
                    filename=uploaded_file.name,
                    file_size=len(file_data),
                    nonce=encode_for_db(encrypted_data['nonce']),
                    tag=encode_for_db(encrypted_data['tag']),
                    uploaded_by=request.user,
                    group=group
                )
                
                # Save encrypted file to disk
                encrypted_file.file.save(
                    f'{encrypted_file.id}.enc',
                    ContentFile(encrypted_data['ciphertext']),
                    save=True
                )
                
                # Encrypt AES key for each group member
                members = group.members.all()
                for member in members:
                    # Get member's RSA public key
                    public_key = member.get_public_key_bytes()
                    
                    if public_key:
                        # Encrypt AES key with member's public key
                        encrypted_aes_key = HybridEncryption.encrypt_aes_key_with_rsa(
                            aes_key, public_key
                        )
                        
                        # Store encrypted AES key for this member
                        FileEncryptionKey.objects.create(
                            file=encrypted_file,
                            user=member,
                            encrypted_aes_key=encode_for_db(encrypted_aes_key)
                        )
                
                messages.success(
                    request,
                    f'File "{uploaded_file.name}" uploaded and encrypted for {members.count()} member(s)!'
                )
                return redirect('groups:detail', pk=group_id)
                
            except Exception as e:
                messages.error(request, f'Error uploading file: {str(e)}')
                # Clean up if error occurred
                if 'encrypted_file' in locals():
                    encrypted_file.file.delete()
                    encrypted_file.delete()
    else:
        form = FileUploadForm()
    
    context = {
        'form': form,
        'group': group,
    }
    return render(request, 'files/upload_file.html', context)


@login_required
def download_file(request, file_id):
    """
    Download and decrypt file
    
    Process:
    1. Check user has access to file
    2. Get FileEncryptionKey for this user+file
    3. Decrypt user's RSA private key with password (from session)
    4. Decrypt AES key with RSA private key
    5. Read encrypted file from disk
    6. Decrypt file with AES key
    7. Return original file
    """
    encrypted_file = get_object_or_404(EncryptedFile, pk=file_id)
    
    # Check if user is member of file's group
    if not encrypted_file.group.is_member(request.user):
        messages.error(request, 'You do not have permission to download this file.')
        return redirect('groups:list')
    
    try:
        # Get FileEncryptionKey for this user and file
        file_key = FileEncryptionKey.objects.get(
            file=encrypted_file,
            user=request.user
        )
        
        # Get user's decrypted RSA private key from session
        private_key_pem = request.session.get('private_key')
        if not private_key_pem:
            messages.error(request, 'Session expired. Please login again.')
            return redirect('users:login')
        
        # Decrypt AES key with RSA private key
        encrypted_aes_key = decode_from_db(file_key.encrypted_aes_key)
        aes_key = HybridEncryption.decrypt_aes_key_with_rsa(
            encrypted_aes_key,
            private_key_pem.encode('utf-8')
        )
        
        # Read encrypted file from disk
        encrypted_file.file.open('rb')
        ciphertext = encrypted_file.file.read()
        encrypted_file.file.close()
        
        # Get nonce and tag
        nonce = decode_from_db(encrypted_file.nonce)
        tag = decode_from_db(encrypted_file.tag)
        
        # Decrypt file with AES
        plaintext = HybridEncryption.decrypt_file_aes(
            ciphertext, aes_key, nonce, tag
        )
        
        # Create response with decrypted file
        response = FileResponse(
            ContentFile(plaintext),
            content_type='application/octet-stream'
        )
        response['Content-Disposition'] = f'attachment; filename="{encrypted_file.filename}"'
        
        return response
        
    except FileEncryptionKey.DoesNotExist:
        messages.error(request, 'You do not have access to this file.')
        return redirect('groups:detail', pk=encrypted_file.group.pk)
    except Exception as e:
        messages.error(request, f'Error downloading file: {str(e)}')
        return redirect('groups:detail', pk=encrypted_file.group.pk)


@login_required
def delete_file(request, file_id):
    """Delete encrypted file"""
    encrypted_file = get_object_or_404(EncryptedFile, pk=file_id)
    
    # Check permissions (uploader or group owner)
    if request.user != encrypted_file.uploaded_by and \
       not encrypted_file.group.is_owner(request.user):
        messages.error(request, 'You do not have permission to delete this file.')
        return redirect('groups:detail', pk=encrypted_file.group.pk)
    
    if request.method == 'POST':
        group_id = encrypted_file.group.pk
        filename = encrypted_file.filename
        
        # Delete file from disk
        if encrypted_file.file:
            encrypted_file.file.delete()
        
        # Delete database record (FileEncryptionKeys cascade delete automatically)
        encrypted_file.delete()
        
        messages.success(request, f'File "{filename}" deleted successfully!')
        return redirect('groups:detail', pk=group_id)
    
    context = {
        'file': encrypted_file,
    }
    return render(request, 'files/delete_file.html', context)


@login_required
def file_list(request):
    """List all files user has access to"""
    # Get all groups user is member of
    user_groups = request.user.file_groups.all()
    
    # Get all files in those groups
    files = EncryptedFile.objects.filter(group__in=user_groups)
    
    context = {
        'files': files,
    }
    return render(request, 'files/file_list.html', context)
