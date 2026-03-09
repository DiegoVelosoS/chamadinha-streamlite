# Chamadinha - Versao Streamlit
Versao web do sistema de reconhecimento facial.

## Objetivo
- Testar a logica central (detectar rosto, reconhecer por embedding, editar dados, gerar planilha de presenca).
- Preparar um relatório de presenças através de imagens recebidas.

## Estrutura
- `app.py`: pagina inicial e setup.
- `pages/1_Cadastro_e_Reconhecimento.py`: upload, deteccao, sugestao de nome e salvamento.
- `pages/2_Galeria_e_Edicao.py`: tabela, mini galeria e edicao de registros.
- `pages/3_Planilha_de_Presenca.py`: consolidacao da planilha e downloads CSV/XLSX.
- `pages/4_Validar_Duplicados.py`: nomeacao de sem nome e validacao de nomes duplicados.
- `core/`: banco, deteccao, reconhecimento e consolidacao.
- `data/rostos.db`: banco SQLite usado por esta versao.

## Executar em localhost (Windows)
Use os comandos abaixo dentro da pasta `streamlit_deploy`:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Se o PowerShell bloquear a ativacao do ambiente virtual, rode:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Depois execute novamente:

```powershell
.\.venv\Scripts\Activate.ps1
python -m streamlit run app.py
```

Ao iniciar, abra no navegador:

- `http://localhost:8501`

## Edicao local (modo desenvolvimento)
- Deixe o Streamlit rodando no terminal.
- Edite arquivos como `app.py`, `pages/*.py` e `core/*.py` no VS Code.
- Salve os arquivos para o Streamlit recarregar automaticamente.
- Se alguma alteracao nao aparecer, use `R` no terminal do Streamlit ou recarregue a pagina no navegador.

## Observacoes
- O reconhecimento automatico depende de `face-recognition`.
- Se `face-recognition` nao estiver disponivel no ambiente, o cadastro continua funcionando, mas nao funcionara o reconhecimento dos rostos salvos.
- Os modelos YuNet/DNN sao baixados automaticamente quando necessario.
- Na pagina inicial (`app.py`), existe a secao **Backup e restauracao do banco (SQLite)**.
	- Clique em **Baixar backup do banco (.db)** ao encerrar a sessao.
	- Na proxima sessao, envie o arquivo em **Restaurar de backup (.db)** e clique em **Aplicar backup enviado**.
	- Esse fluxo e manual e pode ser usado junto com Google Drive (salvando/recuperando o `.db` no Drive).
