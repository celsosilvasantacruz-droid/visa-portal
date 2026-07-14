# Visa Portal

Portal web full-stack para candidaturas a vistos, com backend em Django REST
Framework + Celery, frontend em React, e geração automática de PDF da
candidatura para envio à embaixada.

## Arquitetura

- **backend/** — Django 4.2 + DRF, PostgreSQL, Celery + Redis para tarefas
  assíncronas (geração de PDF e envio de email), encriptação de dados
  sensíveis com `cryptography.Fernet`.
- **frontend/** — React 18, React Router, React Bootstrap, React Hook Form,
  React Dropzone (upload de documentos), React PDF (pré-visualização do PDF
  gerado).
- **nginx** — serve o frontend e faz proxy reverso para a API (`/api`) e
  ficheiros de media (`/media`).
- **docker-compose.yml** — orquestra Postgres, Redis, backend, worker Celery,
  frontend e Nginx.

## Como executar localmente

1. Copia `.env.example` para `.env` e preenche os valores reais
   (`SECRET_KEY`, `ENCRYPTION_KEY`, credenciais de email, etc.):

   ```bash
   cp .env.example .env
   ```

   Para gerar uma `ENCRYPTION_KEY` válida:

   ```bash
   python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
   ```

2. Arranca todos os serviços:

   ```bash
   docker-compose up --build -d
   ```

3. Cria um super utilizador para aceder ao Django Admin:

   ```bash
   docker-compose exec backend python manage.py createsuperuser
   ```

4. Acede à aplicação em `http://localhost` e ao admin em
   `http://localhost/admin/`.

## Notas

- Nunca commits o ficheiro `.env` real (já está no `.gitignore`).
- Os campos de formulário de cada tipo de visto são configurados através do
  Django Admin (`Country` → `VisaType` → `FormField`).
- Os dados de texto submetidos são encriptados antes de serem guardados na
  base de dados.
