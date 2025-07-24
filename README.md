
# Bot de Moderación para Telegram

## Funciones:
- Detecta groserías y emite advertencias.
- Silencia usuarios por 10 minutos cada 5 advertencias (y aumenta 1 min cada vez).
- Notifica a administradores cada 2 advertencias por privado.
- Informa cambios de nombre de usuario o nombre visible.
- Notifica si un usuario sale y luego vuelve al grupo.

## Cómo desplegar en Railway

1. Sube los archivos a Railway o GitHub.
2. Crea una variable de entorno llamada `BOT_TOKEN` con tu token de @BotFather.
3. Asegúrate de que el bot sea administrador en el grupo.
4. ¡Listo!
