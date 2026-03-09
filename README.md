# Chamadinha - Versao Streamlit

Versao web do sistema de reconhecimento facial original, criada em pasta separada para deploy.

## Objetivo

- Nao altera nenhum arquivo do projeto principal.
- Reaproveita a logica central (detectar rosto, reconhecer por embedding, editar dados, gerar planilha de presenca).
- Prepara um fluxo pronto para executar em Streamlit.

## Estrutura

- `app.py`: pagina inicial e setup.
- `pages/1_Cadastro_e_Reconhecimento.py`: upload, deteccao, sugestao de nome e salvamento.
- `pages/2_Galeria_e_Edicao.py`: tabela, mini galeria e edicao de registros.
- `pages/3_Planilha_de_Presenca.py`: consolidacao da planilha e downloads CSV/XLSX.
- `pages/4_Validar_Duplicados.py`: nomeacao de sem nome e validacao de nomes duplicados.
- `core/`: banco, deteccao, reconhecimento e consolidacao.
- `data/rostos.db`: banco SQLite usado por esta versao.

## Executar localmente

No terminal, a partir de `streamlit_deploy`:

```powershell
pip install -r requirements.txt
streamlit run app.py
```

## Deploy no Streamlit

1. Suba a pasta `streamlit_deploy` para o repositorio.
2. No Streamlit Community Cloud, configure:
   - Main file path: `streamlit_deploy/app.py`
   - Python dependencies: `streamlit_deploy/requirements.txt`
3. Para persistencia real de dados em cloud, troque SQLite local por banco externo (PostgreSQL, por exemplo).

## Observacoes

- O reconhecimento automatico depende de `face-recognition`.
- Se `face-recognition` nao estiver disponivel no ambiente, o cadastro continua funcionando, mas sem sugestao automatica de nome.
- Os modelos YuNet/DNN sao baixados automaticamente quando necessario.
