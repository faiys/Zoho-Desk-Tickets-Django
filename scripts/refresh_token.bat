@echo off

echo BAT STARTED >> "C:\Zentegra MFA\Acode\Django\Zdesk\scripts\token.log"
call "C:\Zentegra MFA\Acode\Django\env\Scripts\activate"
cd /d "C:\Zentegra MFA\Acode\Django\Zdesk"
python manage.py refresh_token >> "C:\Zentegra MFA\Acode\Django\Zdesk\scripts\token.log" 2>&1
echo BAT FINISHED >> "C:\Zentegra MFA\Acode\Django\Zdesk\scripts\token.log"
