"""
Encrypted File Models
"""
import uuid
from django.db import models
from django.conf import settings
from groups.models import FileGroup


class EncryptedFile(models.Model):
    """
    Encrypted file storage model
    
    Stores:
    - Encrypted file data (on disk)
    - File metadata (name, size, uploader, group)
    - GCM nonce and authentication tag
    
    Note: AES keys are stored separately in FileEncryptionKey
    """
    
    # UUID primary key (unpredictable IDs for security)
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text='Unique file identifier (UUID)'
    )
    
    # File metadata
    filename = models.CharField(
        max_length=255,
        help_text='Original filename'
    )
    
    file = models.FileField(
        upload_to='encrypted_files/',
        help_text='Encrypted file data on disk'
    )
    
    file_size = models.BigIntegerField(
        help_text='Original file size in bytes (before encryption)'
    )
    
    # Encryption metadata
    nonce = models.CharField(
        max_length=64,
        help_text='AES-GCM nonce (base64 encoded)'
    )
    
    tag = models.CharField(
        max_length=64,
        help_text='AES-GCM authentication tag (base64 encoded)'
    )
    
    # Relationships
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='uploaded_files',
        help_text='User who uploaded this file'
    )
    
    group = models.ForeignKey(
        FileGroup,
        on_delete=models.CASCADE,
        related_name='files',
        help_text='Group this file belongs to'
    )
    
    # Timestamps
    uploaded_at = models.DateTimeField(
        auto_now_add=True
    )
    
    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = 'Encrypted File'
        verbose_name_plural = 'Encrypted Files'
    
    def __str__(self):
        return f"📄 {self.filename}"
    
    def get_size_display(self):
        """Return human-readable file size"""
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"


class FileEncryptionKey(models.Model):
    """
    Stores encrypted AES keys for each user who can access a file
    
    This enables multi-user file access:
    - When file is uploaded, AES key is encrypted with each group member's RSA public key
    - Each user gets their own encrypted copy of the AES key
    - User can decrypt their copy with their RSA private key
    - Then use AES key to decrypt the file
    """
    
    file = models.ForeignKey(
        EncryptedFile,
        on_delete=models.CASCADE,
        related_name='encryption_keys',
        help_text='The encrypted file'
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='file_keys',
        help_text='User who can decrypt this file'
    )
    
    encrypted_aes_key = models.TextField(
        help_text='AES key encrypted with user\'s RSA public key (base64)'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    
    class Meta:
        unique_together = ['file', 'user']
        verbose_name = 'File Encryption Key'
        verbose_name_plural = 'File Encryption Keys'
    
    def __str__(self):
        return f"🔑 {self.file.filename} → {self.user.username}"
