from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from PIL import Image
import os
import uuid
import logging

logger = logging.getLogger(__name__)


class FileManagementService:
    """Consolidated file management service"""
    
    @staticmethod
    def validate_image(file, max_size=5*1024*1024, allowed_formats=['JPEG', 'PNG', 'GIF']):
        """Validate uploaded image file"""
        try:
            # Check file size
            if file.size > max_size:
                return False, f"File size exceeds {max_size // (1024*1024)}MB limit"
            
            # Check file format
            image = Image.open(file)
            if image.format not in allowed_formats:
                return False, f"File format {image.format} not allowed. Allowed formats: {', '.join(allowed_formats)}"
            
            # Check image dimensions
            width, height = image.size
            if width > 2048 or height > 2048:
                return False, "Image dimensions exceed 2048x2048 limit"
            
            return True, "Image is valid"
            
        except Exception as e:
            return False, f"Invalid image file: {str(e)}"
    
    @staticmethod
    def process_and_save_image(file, upload_path, resize_to=None):
        """Process and save image with optional resizing"""
        try:
            # Validate image first
            is_valid, message = FileManagementService.validate_image(file)
            if not is_valid:
                return None, message
            
            # Open image
            image = Image.open(file)
            
            # Convert to RGB if necessary
            if image.mode in ('RGBA', 'LA', 'P'):
                image = image.convert('RGB')
            
            # Resize if specified
            if resize_to:
                image.thumbnail(resize_to, Image.Resampling.LANCZOS)
            
            # Generate unique filename
            file_extension = 'jpg' if image.format == 'JPEG' else image.format.lower()
            unique_filename = f"{uuid.uuid4()}.{file_extension}"
            
            # Create full path
            full_path = os.path.join(upload_path, unique_filename)
            
            # Save image
            output = ContentFile(b"")
            image.save(output, format='JPEG', quality=85)
            output.seek(0)
            
            # Save to storage
            saved_path = default_storage.save(full_path, output)
            
            return saved_path, "Image saved successfully"
            
        except Exception as e:
            logger.error(f"Error processing image: {str(e)}")
            return None, f"Error processing image: {str(e)}"
    
    @staticmethod
    def delete_file(file_path):
        """Delete file from storage"""
        try:
            if default_storage.exists(file_path):
                default_storage.delete(file_path)
                logger.info(f"File deleted: {file_path}")
                return True, "File deleted successfully"
            else:
                return False, "File not found"
        except Exception as e:
            logger.error(f"Error deleting file {file_path}: {str(e)}")
            return False, f"Error deleting file: {str(e)}"
    
    @staticmethod
    def get_file_url(file_path):
        """Get URL for file"""
        try:
            if default_storage.exists(file_path):
                return default_storage.url(file_path)
            else:
                return None
        except Exception as e:
            logger.error(f"Error getting file URL {file_path}: {str(e)}")
            return None
    
    @staticmethod
    def cleanup_orphaned_files():
        """Clean up orphaned files (files not referenced by any model)"""
        try:
            # This would need to be implemented based on your specific needs
            # For now, just log that cleanup was attempted
            logger.info("Orphaned file cleanup attempted")
            return True
        except Exception as e:
            logger.error(f"Error during file cleanup: {str(e)}")
            return False


class DocumentService:
    """Service for document generation and management"""
    
    @staticmethod
    def generate_election_report_csv(election_data):
        """Generate CSV report for election data"""
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['Position', 'Candidate', 'Party', 'Votes', 'Percentage'])
        
        # Write data
        for position_data in election_data:
            for candidate_data in position_data['candidates']:
                writer.writerow([
                    position_data['position'],
                    candidate_data['candidate'],
                    candidate_data['party'],
                    candidate_data['votes'],
                    candidate_data['percentage']
                ])
        
        return output.getvalue()
    
    @staticmethod
    def generate_user_list_csv(users_data):
        """Generate CSV list of users"""
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['Username', 'Email', 'Full Name', 'Student ID', 'Department', 'Course', 'Year Level', 'Verified'])
        
        # Write data
        for user_data in users_data:
            writer.writerow([
                user_data['username'],
                user_data['email'],
                user_data['full_name'],
                user_data['student_id'],
                user_data['department'],
                user_data['course'],
                user_data['year_level'],
                user_data['verified']
            ])
        
        return output.getvalue()
    
    @staticmethod
    def save_document(content, filename, content_type='text/csv'):
        """Save document to storage"""
        try:
            file_content = ContentFile(content.encode('utf-8'))
            saved_path = default_storage.save(filename, file_content)
            return saved_path, "Document saved successfully"
        except Exception as e:
            logger.error(f"Error saving document: {str(e)}")
            return None, f"Error saving document: {str(e)}"


def get_upload_path(instance, filename):
    """Generate upload path for files"""
    # Extract file extension
    ext = filename.split('.')[-1]
    
    # Generate unique filename
    unique_filename = f"{uuid.uuid4()}.{ext}"
    
    # Determine upload directory based on instance type
    if hasattr(instance, 'user') and hasattr(instance, 'photo'):
        return f"candidate_photos/{unique_filename}"
    elif hasattr(instance, 'avatar'):
        return f"profile_photos/{unique_filename}"
    elif hasattr(instance, 'logo'):
        return f"party_logos/{unique_filename}"
    else:
        return f"uploads/{unique_filename}"
