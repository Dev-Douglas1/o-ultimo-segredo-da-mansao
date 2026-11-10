# O Último Segredo da Mansão

Escape Room de investigação em pixel art, desenvolvido em Python 3 com Tkinter e arquivos JSON.

## Requisitos
- Python 3.12 ou superior
- Tkinter (incluído normalmente no instalador oficial do Python para Windows)
- Pillow para gerar novamente os recursos gráficos e sonoros, caso necessário

## Executar no Windows

```powershell
python -m pip install -r requirements.txt
python gerar_assets.py
python main.py
```

O jogo também possui modo de terminal para demonstrar os requisitos escolares de `input()`, `while`, `for`, condicionais e persistência JSON:

```powershell
python main.py --terminal
```

## Controles
- Mouse: investigar objetos
- I: inventário
- F1: solicitar pista
- ESC: voltar ao menu

## Estrutura
- `main.py`: motor do jogo e interface gráfica
- `dados/enigmas.json`: salas, objetos, pistas e códigos
- `dados/progresso.json`: estado salvo da partida
- `dados/historico.json`: resultados anteriores
- `assets/`: cenários e sons em pixel art
- `gerar_assets.py`: recria os recursos locais

Os arquivos JSON fazem parte do funcionamento do jogo: são carregados, atualizados e consultados durante as partidas. O progresso e o histórico persistem após fechar o programa.

## Observação
Este projeto foi desenvolvido como trabalho escolar. As imagens e os efeitos sonoros são gerados pelo script incluído; não são utilizados recursos de terceiros protegidos.
