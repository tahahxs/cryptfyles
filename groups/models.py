"""
FileGroup Model for Encrypted File Sharing
"""
from django.db import models
from django.conf import settings


class FileGroup(models.Model):
    """
    A group where users can share encrypted files
    
    Fields:
    - name: Unique group name
    - description: What the group is for
    - created_by: User who created the group (owner)
    - members: Users who can access files in this group
    - created_at: When group was created
    """
    
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Unique name for this group"
    )
    
    description = models.TextField(
        blank=True,
        help_text="Description of what this group is for"
    )
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_groups',
        help_text="User who created this group"
    )
    
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='file_groups',
        blank=True,
        help_text="Users who can access files in this group"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'File Group'
        verbose_name_plural = 'File Groups'
    
    def __str__(self):
        return f"📁 {self.name}"
    
    def member_count(self):
        """Return number of members in the group"""
        return self.members.count()
    
    def is_member(self, user):
        """Check if user is a member of this group"""
        return self.members.filter(id=user.id).exists()
    
    def is_owner(self, user):
        """Check if user is the owner of this group"""
        return self.created_by == user
    
    def can_manage(self, user):
        """Check if user can manage (edit/delete) this group"""
        return self.is_owner(user) or user.is_staff
    
    def add_member(self, user):
        """Add a user to the group"""
        if not self.is_member(user):
            self.members.add(user)
    
    def remove_member(self, user):
        """Remove a user from the group"""
        if self.is_member(user) and not self.is_owner(user):
            self.members.remove(user)
