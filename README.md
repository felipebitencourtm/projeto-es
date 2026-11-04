projeto_koilingo/
├── data/                      # Diretório contendo os arquivos de persistência
│   ├── usuarios.json          # Dados de Usuario, Aluno, Admin, Amizades
│   ├── conteudos.json         # Dados de Idioma, Unidade, Licao, Exercicios
│   └── progresso.json         # Dados de ProgressoIdioma, SessaoSrs, EstadoRevisao
│
├── src/                       # Código fonte principal
│   ├── main.py                # Ponto de entrada da aplicação (inicializa o Tkinter)
│   │
│   ├── models/                # Representação exata das classes do diagrama "classes.png"
│   │   ├── profile.py         # Classes: Usuario, Aluno, Admin, Amizade, PedidoDeAmizade
│   │   ├── course.py          # Classes: Idioma, Unidade, Licao
│   │   ├── progress.py        # Classes: ProgressoIdioma, ProgressoLicao, SessaoSrs, EstadoRevisao
│   │   └── practice.py        # Classes: Exercicio (e heranças), Revisao, Alternativa, PontoGramatical
│   │
│   ├── repositories/          # Lógica de leitura e escrita dos arquivos JSON
│   │   ├── base_repository.py # Funções genéricas de ler/escrever arquivos .json
│   │   ├── user_repo.py       # Interação específica com usuarios.json
│   │   ├── course_repo.py     # Interação específica com conteudos.json
│   │   └── progress_repo.py   # Interação específica com progresso.json
│   │
│   ├── controllers/           # Orquestração entre a UI, Models e Repositories
│   │   ├── auth_controller.py     # Lógica de login, registro, autenticação
│   │   ├── study_controller.py    # Lógica de iniciar exercícios, responder, SRS (repetição espaçada)
│   │   └── social_controller.py   # Lógica de amizades e ranking
│   │
│   └── ui/                    # Telas e componentes do Frontend simplificado em Tkinter
│       ├── app_window.py      # Janela principal do Tkinter, gerenciador de frames
│       ├── login_view.py      # Tela de login e cadastro
│       ├── dashboard_view.py  # Tela principal do aluno (progresso, streak, iniciar lição)
│       └── exercise_view.py   # Telas dinâmicas para os tipos de exercícios (Tradução, Alternativas, etc.)
│
├── README.md                  # Documentação básica do projeto
