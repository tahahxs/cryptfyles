"""
Group Views
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import FileGroup
from .forms import GroupCreateForm, GroupEditForm, AddMemberForm
from users.models import CustomUser


@login_required
def group_list(request):
    """Display all groups the user is a member of or owns"""
    # Groups owned by user
    owned_groups = FileGroup.objects.filter(created_by=request.user)
    
    # Groups user is a member of
    member_groups = request.user.file_groups.exclude(created_by=request.user)
    
    context = {
        'owned_groups': owned_groups,
        'member_groups': member_groups,
    }
    return render(request, 'groups/group_list.html', context)


@login_required
def group_create(request):
    """Create a new group"""
    if request.method == 'POST':
        form = GroupCreateForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.created_by = request.user
            group.save()
            
            # Add creator as first member
            group.members.add(request.user)
            
            messages.success(request, f'Group "{group.name}" created successfully!')
            return redirect('groups:detail', pk=group.pk)
    else:
        form = GroupCreateForm()
    
    return render(request, 'groups/group_create.html', {'form': form})


@login_required
def group_detail(request, pk):
    """View group details and members"""
    group = get_object_or_404(FileGroup, pk=pk)
    
    # Check if user is a member or owner
    if not group.is_member(request.user) and not group.is_owner(request.user):
        messages.error(request, 'You do not have access to this group.')
        return redirect('groups:list')
    
    # Get all members
    members = group.members.all()
    
    # Check if user can manage group
    can_manage = group.can_manage(request.user)
    
    context = {
        'group': group,
        'members': members,
        'can_manage': can_manage,
    }
    return render(request, 'groups/group_detail.html', context)


@login_required
def group_edit(request, pk):
    """Edit group details"""
    group = get_object_or_404(FileGroup, pk=pk)
    
    # Check if user can manage group
    if not group.can_manage(request.user):
        messages.error(request, 'You do not have permission to edit this group.')
        return redirect('groups:detail', pk=pk)
    
    if request.method == 'POST':
        form = GroupEditForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            messages.success(request, f'Group "{group.name}" updated successfully!')
            return redirect('groups:detail', pk=pk)
    else:
        form = GroupEditForm(instance=group)
    
    context = {
        'form': form,
        'group': group,
    }
    return render(request, 'groups/group_edit.html', context)


@login_required
def group_delete(request, pk):
    """Delete a group"""
    group = get_object_or_404(FileGroup, pk=pk)
    
    # Check if user can manage group
    if not group.can_manage(request.user):
        messages.error(request, 'You do not have permission to delete this group.')
        return redirect('groups:detail', pk=pk)
    
    if request.method == 'POST':
        group_name = group.name
        group.delete()
        messages.success(request, f'Group "{group_name}" deleted successfully!')
        return redirect('groups:list')
    
    return render(request, 'groups/group_delete.html', {'group': group})


@login_required
def add_member(request, pk):
    """Add a member to a group"""
    group = get_object_or_404(FileGroup, pk=pk)
    
    # Check if user can manage group
    if not group.can_manage(request.user):
        messages.error(request, 'You do not have permission to add members.')
        return redirect('groups:detail', pk=pk)
    
    if request.method == 'POST':
        form = AddMemberForm(request.POST, group=group)
        if form.is_valid():
            username = form.cleaned_data['username']
            user = CustomUser.objects.get(username=username)
            group.add_member(user)
            messages.success(request, f'{username} added to group "{group.name}"!')
            return redirect('groups:detail', pk=pk)
    else:
        form = AddMemberForm(group=group)
    
    context = {
        'form': form,
        'group': group,
    }
    return render(request, 'groups/add_member.html', context)


@login_required
def remove_member(request, pk, user_id):
    """Remove a member from a group"""
    group = get_object_or_404(FileGroup, pk=pk)
    user_to_remove = get_object_or_404(CustomUser, pk=user_id)
    
    # Check if requester can manage group
    if not group.can_manage(request.user):
        messages.error(request, 'You do not have permission to remove members.')
        return redirect('groups:detail', pk=pk)
    
    # Don't allow removing the owner
    if group.is_owner(user_to_remove):
        messages.error(request, 'Cannot remove the group owner.')
        return redirect('groups:detail', pk=pk)
    
    if request.method == 'POST':
        group.remove_member(user_to_remove)
        messages.success(request, f'{user_to_remove.username} removed from group "{group.name}"!')
        return redirect('groups:detail', pk=pk)
    
    context = {
        'group': group,
        'user_to_remove': user_to_remove,
    }
    return render(request, 'groups/remove_member.html', context)
