# Audio Extract App

Aplicativo interno em Django para receber links ou arquivos de video, extrair audio e gerar transcricao quando o backend de transcricao estiver instalado.

## Recursos

- Upload de video local.
- Link de video suportado pelo `yt-dlp`, incluindo YouTube.
- Extracao de audio com `ffmpeg`.
- Registro de tarefas no banco.
- Transcricao opcional com Whisper local.
- Interface simples para acompanhar status e baixar resultados.
- Preparado para Supabase Postgres e deploy via GitHub.

## Rodando localmente

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py runserver
```

Para transcricao local:

```bash
pip install -r requirements-transcription.txt
```

O `ffmpeg` precisa estar instalado e disponivel no PATH.

No Windows, tambem pode usar um FFmpeg portatil dentro de `.tools/ffmpeg/bin/ffmpeg.exe`; o app detecta esse caminho automaticamente. Se quiser apontar outro local, use:

```env
FFMPEG_BINARY=C:\caminho\para\ffmpeg.exe
```

## Supabase

Crie um projeto no Supabase, copie a string de conexao do Postgres e coloque no `.env`:

```env
DATABASE_URL=postgresql://...
```

Depois rode:

```bash
python manage.py migrate
```

## GitHub e deploy

Este projeto ja inclui workflow de CI em `.github/workflows/ci.yml`.

GitHub Pages nao roda Django. Para hospedagem gratis, conecte o repositorio a um servico como Render, Koyeb, Fly.io ou Railway e configure as variaveis de ambiente do `.env.example`.

Em ambientes pequenos, a transcricao local pode ser pesada. Para MVP em hosting gratis, comece com extracao de audio e teste a transcricao com videos curtos.

Se a plataforma permitir worker separado, use o processo `worker` do `Procfile`. Se nao permitir, o app tambem dispara o processamento automaticamente via thread quando `JOB_AUTO_START=True`.

O `Dockerfile` ja instala `ffmpeg` e as dependencias de transcricao, entao prefira deploy por Docker quando a plataforma permitir. O arquivo `render.yaml` deixa a base pronta para criar um Blueprint no Render conectado ao GitHub.

### Deploy no Render com Supabase

1. No Supabase, copie a string Postgres em `Project Settings > Database > Connection string > URI`.
2. No Render, crie um Blueprint ou Web Service conectado ao repositorio GitHub.
3. Se criar manualmente, selecione `Docker` como runtime. O `Dockerfile` fica na raiz do repo.
4. Configure as variaveis de ambiente:

```env
SECRET_KEY=uma-chave-grande-e-segura
DEBUG=False
ALLOWED_HOSTS=seu-app.onrender.com
CSRF_TRUSTED_ORIGINS=https://seu-app.onrender.com
DATABASE_URL=postgresql://...
SUPABASE_URL=https://bgubettsljljqxohfzeg.supabase.co
SUPABASE_PUBLISHABLE_KEY=sua-chave-publica
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=seu-email@empresa.com
DJANGO_SUPERUSER_PASSWORD=uma-senha-forte
JOB_AUTO_START=True
```

Na primeira inicializacao, o container roda migrations e cria o admin inicial automaticamente quando as variaveis `DJANGO_SUPERUSER_*` existem.

Fluxo sugerido:

```bash
git init
git add .
git commit -m "Initial Django audio extractor"
git branch -M main
git remote add origin https://github.com/SEU-USUARIO/audio-extract-app.git
git push -u origin main
```
