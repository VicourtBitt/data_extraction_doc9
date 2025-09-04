# Desafio Técnico DOC9: Extração de Dados e Download de Faturas
### Introdução
O projeto tem como foco cumprir com o desafio proposto pela DOC9 para o processo seletivo de Desenvolvedor RPA Junior, do qual tinha como enunciado:

> O objetivo deste desafio é criar um fluxo de trabalho que fará a leitura de todas as linhas da tabela e fará o download das respectivas faturas.
Dos itens de fatura você deverá extrair o ID da Fatura, Data da Fatura, URL da fatura.
Você terá que construir um CSV e salvar as faturas numa pasta. Considere apenas para as faturas cuja Data de Vencimento já passou ou é hoje (o site atualiza as datas de forma dinâmica.).

Além disso, haviam algumas flags importantes que ressaltavam:
- Funcionalidade (Atendimento da necessidade e do escopo);
- Performance (Velocidade de Execução (*));
- Código/Boas Práticas (Boas práticas e documentação)

##### Vídeo de Apresentação do Projeto
https://www.youtube.com/watch?v=uBVyv_IAhH8

##### Observação:
Sobre estas flags, acho importante ressaltar o seguinte:
- **Perfomance**: Eu penso que, a questão de tempo de execução do código não contabiliza o tempo de download, já que o csv é finalizado muito antes e é inviável em um cenário real depender do tempo de resposta de um servidor, porém, posso estar errado e peço perdão quando a isso.
- **Código/Boas Práticas**: Modularizei o código com um utils (auxiliar utilitário) e coloquei as variáveis dentro de um **.env** que são resgatados pelo **python-dotenv**, sobre documentação, utilizei um estilo similar ao Sphinx que mais verboso porém legível.

### Soluções Desenvolvidas
Devido os requisitos das flags (não só os requisitos técnicos), idealizei duas soluções, porém criei uma alternativa para tentar minimizar o tempo da **Performance**, o que é drasticamente visível mais pra frente, dentre as soluções temos:
- **headless.py (Abordagem com Selenium)**: Como o próprio nome diz, utilizamos uma instância headless para não ter que abrir o WebDriver visivelmente na execução do processo, rodando ele em segundo plano, o que é prática/padrão de mercado para extrações como essa.
- **api.py (Abordagem com Requests)**: Depois de algum tempo no desafio, notei que o site não é populado como SSG (Static Site Generation) como presente em sites como em: **https://webscraper.io/test-sites/e-commerce/static/computers/laptops** mas sim realizava uma chamada a uma API aberta (sem chave, descobri pelo DevTools), o que tornava possível consumir direto da fonte.
- **api_threading (Abordagem Alternativa Performática Concorrente)**: Por mais que as últimas duas suprissem a necessidade, fui um pouco mais a fundo e utilizei uma abordagem multi-thread (com ajuda de agentes, já fazia um tempo desde que mexi com threads), que se provou realmente a otimização mais efetiva.

Teremos um benchmark no final do README

### Tecnologias Utilizadas
No desafio tinhamos alguns requisitos técnicos possíveis, porém com o `etc...` dentro deles eu adicionei duas bibliotecas, porém, as bibliotecas gerais foram:

- **requests**: Para fazer as requisições direto a API;
- **python-dotenv**: Gerenciar as variáveis de ambiente.
- **pandas** (adicionado): Para manipulação dos dados e criação de CSV's sem muito overhead em lógica, já uso a ferramenta no dia-a-dia;

Dentre as específicas em cada solução:

`headless.py:`
- **Selenium**: Para controlar o navegador e fazer as interações/automações;
- **webdriver-manager** (adicionado): Gerenciar automaticamente o Chrome WebDriver no computador em que o código estiver rodando;

`api_threading.py:`
- **concurrent.futures**: Um módulo nativo do Python que ajuda a fazer tarefas de forma paralela;

### Configurações do Ambiente
Aqui, vamos fazer o passo-a-passo para criar um ambiente virtual e as variáveis do ambiente.

**1° Criar o Ambiente Virtual**: Permite separarmos dependências para diferentes projetos.
```
    # Crie o ambiente virtual
    python3 -m venv .venv (Linux/macOS)
    ou
    python -m venv .venv (Windows)

    # Ative o ambiente (Linux/macOS)
    source .venv/bin/activate

    # Ative o ambiente (Windows)
    .\.venv\Scripts\activate 
```

**2° Instalar as Dependências**: Todos os modulos/bibliotecas de terceiros presentes em `requirements.txt`
```
    pip install -r requirements.txt
```

**3° Configurar as Variáveis de Ambiente**: Criar um arquivo chamado .env na raiz do projeto para deixar elas acessíveis aos outros scripts.
```
API_URL=https://rpachallengeocr.azurewebsites.net/seed
BASE_URL=https://rpachallengeocr.azurewebsites.net/
DOWNLOAD_FOLDER=invoices
CSV_NAME=filtered_invoices.csv
TIMEOUT=10
```

### Como Executar os Códigos
Depois de ter feito todas essas configurações, você pode executar o código de duas formas, pelo terminal ou usando alguma extensão do VSCode/IDE de sua preferência, se você utiliza o VSCode, recomendaria o **CodeRunner**.
Pelo terminal:
```
# Para executar a solução com Selenium Headless
python headless.py
ou
python3 headless.py

# Para executar a solução com API e downloads sequenciais
python api.py
ou
python3 api.py

# Para executar a solução otimizada com API e downloads em paralelo
python api_threading.py
ou
python3 api_threading.py
```

Quando os códigos terminarem a execução você terá 3 coisas:
- **No terminal**: A indicação de quanto tempo o código levou para rodar completo (extração e download somados);
- **Na raiz da pasta**: Um diretório novo (invoices) onde estarão todas as faturas (em JPG) e um csv chamado `filtered_invoices`

### Benchmarking
Sobre os tempos de execução totais, `headless.py` foi o código mais lento, porém era o esperado afinal, tinha de abrir a instância do navegador e utilizar dos tempos de espera para DOM estar populado, `api.py` foi a solução intermediária, consumia direto da API que populava o FrontEnd, o que tornava a execução **44% mais rápida**, por último, temos o `api_threading.py` que roda **73% mais rápido** que o `api.py` e **85% mais rápido** que o `headless.py`.  

| Solução | Tempo de Execução (extração + download) |
|---------|------------------|
| headless.py | 18.19 segundos |
| api.py | 10.13 segundos (44.3%+ rápido) |
| api_threading.py | 2.6897 segundos (73.4% / 85.2%) |

---

Sobre os tempos de execução só de extração, `headless.py` foi o código mais lento, porém era o esperado afinal, tinha de abrir a instância do navegador e utilizar dos tempos de espera para DOM estar populado, `api.py` foi a solução intermediária, consumia direto da API que populava o FrontEnd, o que tornava a execução **78% mais rápida**, por último, temos o `api_threading.py` que roda de forma identica ao o `api.py` e **78% mais rápido** que o `headless.py` que é a mesma performance do `api.py`.

| Solução | Tempo de Execução (somente extração) |
|---------|------------------|
| headless.py | 5.10 segundos |
| api.py | 1.09 segundos (78.6%+ rápido) |
| api_threading.py | 1.10 segundos (identicos basicamente / 78.4%) |