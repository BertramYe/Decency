# 这里面进行封装一些本网站所使用到的公共的组件
import threading
# 导入邮件发送模块
from django.core.mail import send_mail
# 导入邮件发送参数
from decency import settings
# 为了提高网站运行的效率，在这里我们单独开一个线程，进行邮件的发送

class SendEmail(threading.Thread):
    def __init__(self,email_sending_for,target_email,email_text):
        super().__init__()
        self.email_sending_for=email_sending_for
        self.target_email = target_email
        self.email_text = email_text

    def run(self):
        if self.email_sending_for == "Comment_Tips":
            subject = "有新的评论/回复需要审核处理"
            send_mail(
                subject,
                "",
                settings.EMAIL_HOST_USER,
                [self.target_email],
                fail_silently=False,
                # 将html的内容转换成string，然后传进来即可
                html_message=self.email_text
            ) 
        if self.email_sending_for =="Verification_Code":
            subject = "邮箱绑定"
            email_content =  f'邮箱绑定的验证码为:{self.email_text}（单次验证），请输入验证码，完成邮箱绑定！'
            send_mail(
                # 邮件主题
                subject,
                # 邮件内容
                email_content,
                # 发送邮件的邮箱地址
                # 'XXXX@qq.com',
                settings.EMAIL_HOST_USER,
                # 目标邮件，可以是多个邮件，因为目标邮件是一个列表
                [self.target_email], 
                # 是否忽略邮箱发送过程中的错误      
                fail_silently=False,
                )
            # 邮件发送成功给前端反馈一个状态信息