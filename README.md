# O Último Segredo da Mansão — Escape Room em Pixel Art

Jogo escolar original em Python 3, com interface gráfica Tkinter, arte pixelada em primeira pessoa (cenas fixas), objetos clicáveis, inventário, códigos, dicas, contagem regressiva, conquistas, três finais e arquivos JSON persistentes.

## Instalação no Windows com VS Code

1. Extraia o arquivo ZIP. Abra a pasta `mansao_ultimo_segredo` no VS Code.
2. Confira se `main.py`, `assets/` e `dados/` estão nessa pasta.
3. Abra **Terminal > Novo Terminal**.
4. Execute `python main.py` (ou `py main.py`).
5. Digite seu nome e comece a explorar a mansão.

**Não é necessário instalar bibliotecas externas.** Tkinter normalmente acompanha o Python para Windows. Os arquivos de arte e som já estão incluídos.

## Controles

- **Mouse**: clicar nos objetos delimitados em dourado.
- **F1**: solicitar uma pista (aumenta o contador de dicas).
- **I**: visualizar inventário.
- **ESC**: voltar ao menu; o progresso permanece salvo.
- **Salvar**: grava os dados em `dados/progresso.json`.
- **Continuar**: recupera o progresso salvo, inclusive inventário e tempo.

## Modo de terminal com input()

Para demonstrar explicitamente `input()`, `while`, `for`, `if`, `elif`, `else`:

```powershell
python main.py --terminal
```

O modo terminal usa o mesmo motor e os mesmos JSON, porém não exibe interface gráfica. Ele permite navegar, investigar, digitar códigos, pedir dicas e escolher o final. A contagem regressiva é aplicada no modo gráfico; no terminal o tempo salvo é preservado.

## Estrutura

```
mansao_ultimo_segredo/
├── main.py
├── assets/
│   ├── capa.png
│   ├── hall.png
│   ├── biblioteca.png
│   ├── escritorio.png
│   ├── porao.png
│   ├── camara.png
│   ├── ambiente.wav
│   ├── porta.wav
│   ├── acerto.wav
│   └── erro.wav
├── dados/
│   ├── enigmas.json
│   ├── progresso.json
│   └── historico.json
├── gerar_assets.py
├── requirements.txt
└── README.md
```

O jogo lê `enigmas.json` para montar as cinco salas e seus objetos. `progresso.json` é atualizado durante a exploração e permite continuar após fechar o programa. `historico.json` registra resultados finais. Todos usam listas, objetos e pares chave-valor.

`gerar_assets.py` é opcional e só serve para **recriar** as imagens e os sons originais. Se quiser executá-lo, instale `Pillow` com `python -m pip install pillow`. **Não é necessário executá-lo para jogar.**

## Finais

- **Verdade revelada**: sair com o diário e a prova da conspiração.
- **Fuga**: sair sem revelar o segredo.
- **Derrota**: esgotar quatro tentativas em um código ou deixar o tempo acabar.

## Roteiro de demonstração ao professor

1. Abra `dados/enigmas.json` e mostre a lista de cinco salas, os objetos e os códigos.
2. Execute `python main.py` e inicie uma partida.
3. Clique em objetos e recolha uma chave para demonstrar o inventário.
4. Peça uma dica e teste uma senha incorreta.
5. Salve, feche o jogo, abra novamente e use **Continuar**.
6. Mostre as alterações em `dados/progresso.json`.
7. Complete o jogo e mostre `dados/historico.json`.
8. Execute `python main.py --terminal` para demonstrar `input()` e o `while` diretamente.

## Atenção

A arte é uma composição pixelada original criada para este projeto. A visão em primeira pessoa é **point-and-click com cenas estáticas**, não um mundo 3D navegável. No Windows, a trilha e os efeitos WAV usam `winsound`; em outros sistemas o jogo funciona, mas o áudio pode ser substituído pelo sinal sonoro da interface.


## Atualização visual e narrativa

A versão atual inclui uma abertura narrativa em três quadros, com texto revelado gradualmente, antes de iniciar a exploração. Durante as salas, pequenos pixels de poeira flutuam e a iluminação pulsa discretamente para dar vida aos cenários. As áreas de clique são invisíveis; o cursor muda ao passar sobre objetos interativos. O cronômetro atualiza sem redesenhar toda a cena.


## Direção visual e referências

A direção visual foi refinada com base em convenções de aventuras point-and-click de terror: cenários fixos com composição legível, objetos integrados à narrativa, atmosfera por chuva/luz/som e pistas ambientais. Referências de estudo:
- The Mansion (pixel-art horror adventure): https://yusaku-nakayama.itch.io/the-mansion-demo
- A Room Beyond (pixel graphics, point-and-click e atmosfera): https://www.aroombeyond.com/
- The Horror of Salazar House (aventura de mansão, investigação e múltiplos finais): https://www.grimoireofhorror.com/the-banshee/the-horror-of-salazar-house-game-review/

As imagens incluídas neste projeto foram desenhadas para este jogo e não são extraídas desses títulos.


## Versão refinada — narrativa e animações

- A tela de introdução agora mostra os três blocos de história imediatamente, sem depender do fim de uma animação de digitação para revelar o texto.
- Abertura com chuva animada e relâmpagos ocasionais.
- Cenários de cinco salas redesenhados em pixel art com mais detalhes, profundidade e objetos ambientais.
- Poeira flutuante durante a exploração, oscilação de chama no escritório/porão e aparição breve de uma silhueta no hall.
- Corrigido o tratamento do movimento do mouse sobre os botões e objetos: a lista de áreas clicáveis contém dois formatos de registro e agora ambos são tratados corretamente.
- O menu usa a nova arte exterior da mansão.

### Atualização
Feche a versão anterior, extraia este ZIP em uma pasta nova e execute `python main.py` dentro da pasta que contém o arquivo principal. Não misture os arquivos antigos com os novos.


## Dificuldade e narrativa

A campanha oferece 20 minutos por partida, três tentativas por mecanismo, penalidade de 1 minuto por erro e custo de 1 minuto e 30 segundos por dica. O nível de alerta aumenta com erros. As pistas são ambientais e exigem relacionar informações encontradas em salas diferentes.


## Mecanismos interativos inspirados em aventuras de caixas de enigmas

Os cofres e painéis de senha agora abrem uma tela própria de mecanismo. O jogador gira discos numéricos ou alfabéticos com os botões de seta e precisa montar a combinação antes de testar. O cronômetro continua ativo enquanto o mecanismo está aberto; erros aplicam as penalidades normais do jogo. Esta implementação é uma adaptação 2D original para Tkinter, não uma reprodução dos recursos 3D ou dos controles por toque de The Room.
