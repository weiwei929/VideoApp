from django.contrib.auth.models import User
from ..models import PikpakAccount
import logging

logger = logging.getLogger(__name__)

class AuthService:
    """
    处理PikPak账户的认证相关功能
    """
    
    @staticmethod
    def save_webdav_credentials(user, webdav_url, webdav_username, webdav_password):
        """
        保存WebDAV凭证到用户账号
        """
        try:
            # 查找或创建PikpakAccount
            account, created = PikpakAccount.objects.update_or_create(
                user=user,
                defaults={
                    'email': user.email if user.email else f"user_{user.id}@example.com",
                    'webdav_url': webdav_url,
                    'webdav_username': webdav_username,
                    'webdav_password': webdav_password
                }
            )
            return {'success': True, 'account': account}
        except Exception as e:
            logger.error(f"保存WebDAV凭证失败: {str(e)}")
            return {'success': False, 'message': f'保存凭证失败: {str(e)}'}
    
    @staticmethod
    def get_webdav_credentials(user):
        """
        获取用户的WebDAV凭证
        """
        try:
            account = PikpakAccount.objects.get(user=user)
            if account.is_webdav_configured():
                return {
                    'success': True,
                    'webdav_url': account.webdav_url,
                    'webdav_username': account.webdav_username,
                    'webdav_password': account.webdav_password
                }
            return {'success': False, 'message': 'WebDAV未配置'}
        except PikpakAccount.DoesNotExist:
            return {'success': False, 'message': '找不到账号信息'}
        except Exception as e:
            logger.error(f"获取WebDAV凭证失败: {str(e)}")
            return {'success': False, 'message': f'获取凭证失败: {str(e)}'}
    
    @staticmethod
    def get_webdav_credentials_from_session(request):
        """
        从会话中获取WebDAV凭证
        支持未登录用户使用临时凭证
        """
        # 已登录用户从数据库获取
        if request.user.is_authenticated:
            return AuthService.get_webdav_credentials(request.user)
        
        # 未登录用户从会话中获取
        credentials = request.session.get('webdav_credentials', {})
        if credentials and all(k in credentials for k in ['url', 'username', 'password']):
            return {
                'success': True,
                'webdav_url': credentials['url'],
                'webdav_username': credentials['username'],
                'webdav_password': credentials['password']
            }
        
        return {'success': False, 'message': '未找到WebDAV凭证'}
    
    @staticmethod
    def save_webdav_credentials_to_session(request, webdav_url, webdav_username, webdav_password):
        """
        保存WebDAV凭证到会话
        用于未登录用户
        """
        request.session['webdav_credentials'] = {
            'url': webdav_url,
            'username': webdav_username,
            'password': webdav_password
        }
        return {'success': True}
