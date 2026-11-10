"""O Último Segredo da Mansão — Escape Room escolar, Python 3.10+.
Interface Tkinter com arte pixelada, sons WAV originais e persistência JSON.
Modo --terminal demonstra input(), while, for, if/elif/else.
"""
import json
import os
import random
import sys
import time
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import messagebox, simpledialog

ROOT = Path(__file__).resolve().parent
DATA = ROOT / 'dados'
ASSETS = ROOT / 'assets'


def ler(nome, padrao):
    try:
        with (DATA / nome).open('r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return padrao


def gravar(nome, dados):
    destino = DATA / nome
    temporario = destino.with_suffix('.tmp')
    with temporario.open('w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    os.replace(temporario, destino)


def estado_novo(nome, segundos):
    return dict(jogador=nome, status='jogando', sala=0, inventario=[], vistos=[],
                resolvidos=[], tentativas={}, dicas=0, tempo_restante=segundos,
                conquistas=[], alerta=0, campanha={}, inicio=datetime.now().isoformat(timespec='seconds'))


class Motor:
    def __init__(self):
        self.dados = ler('enigmas.json', {'salas': [], 'conquistas': [], 'duracao_segundos': 1500})
        if len(self.dados['salas']) < 5:
            raise ValueError('enigmas.json deve conter ao menos cinco salas.')
        self.estado = ler('progresso.json', estado_novo('', 1500))
        self.historico = ler('historico.json', {'partidas': []})
        if self.estado.get('status') == 'jogando' and self.estado.get('campanha'):
            self.aplicar_campanha_salva()

    @property
    def sala(self):
        return self.dados['salas'][self.estado['sala']]

    def salvar(self):
        gravar('progresso.json', self.estado)

    def gerar_campanha(self):
        ano = random.choice([1903, 1911, 1924, 1936, 1948, 1957, 1969, 1978, 1987, 1996])
        codigo_cofre = ''.join(str(n) for n in random.sample(range(1, 10), 4))
        codigo_armario = ''.join(str(n) for n in random.sample(range(1, 10), 3))
        alfabeto = 'ABCDEFGHJKLMNPQRSTUVWXYZ'
        codigo_painel = ''.join(random.choice(alfabeto) for _ in range(3))
        casos = [
            ('Helena Valença', 'o mordomo', 'desvio da herança'),
            ('Artur Valença', 'a governanta', 'um incêndio criminoso'),
            ('Cecília Valença', 'o médico da família', 'o desaparecimento do herdeiro'),
            ('Tomás Valença', 'o advogado', 'a falsificação do testamento')
        ]
        desaparecida, suspeito, crime = random.choice(casos)
        return {
            'ano': ano, 'codigo_cofre': codigo_cofre,
            'codigo_armario': codigo_armario, 'codigo_painel': codigo_painel,
            'tipos': [random.choice(['discos', 'teclado', 'sequencia']) for _ in range(3)],
            'desaparecida': desaparecida, 'suspeito': suspeito, 'crime': crime,
            'selo': random.choice(['corvo', 'ampulheta', 'lua partida', 'mariposa']),
            'frase': random.choice([
                'Quando o relógio silenciar, procure aquilo que não projeta sombra.',
                'A casa guarda melhor seus segredos atrás do que parece comum.',
                'Três testemunhas mentiram. A quarta deixou uma marca.',
                'A ordem dos acontecimentos vale mais que a ordem dos números.'
            ])
        }

    def aplicar_campanha_salva(self):
        campanha = self.estado['campanha']
        codigos = {'cofre': 'codigo_cofre', 'armario': 'codigo_armario', 'painel': 'codigo_painel'}
        for sala in self.dados['salas']:
            for obj in sala['objetos']:
                if obj['id'] in codigos:
                    obj['codigo'] = campanha[codigos[obj['id']]]
                if obj['id'] == 'retrato':
                    obj['texto'] = f"Fotografia datada de {campanha['ano']}. O selo da família é uma {campanha['selo']}."
                elif obj['id'] == 'livro':
                    obj['texto'] = f"Anotação: {campanha['desaparecida']} desapareceu em {campanha['ano']}. Nas margens, os números aparecem separados por pontos: {' · '.join(campanha['codigo_cofre'])}."
                elif obj['id'] == 'carta':
                    obj['texto'] = f"Bilhete: 'A sequência dos sinos foi {', '.join(campanha['codigo_armario'])}. Não ignore a ordem dos acontecimentos.'"
                elif obj['id'] == 'vela':
                    obj['texto'] = "Na cera endurecida há três letras: " + ' — '.join(campanha['codigo_painel']) + ". A marca da chama indica a ordem de leitura."
                elif obj['id'] == 'diario':
                    obj['texto'] = f"As páginas acusam {campanha['suspeito']} de encobrir {campanha['crime']}. A última anotação diz: {campanha['frase']}"
                elif obj['id'] == 'altar':
                    obj['texto'] = f"O selo {campanha['selo']} está entalhado no altar. A frase: '{campanha['frase']}'"

    def novo(self, nome):
        self.estado = estado_novo(nome, self.dados['duracao_segundos'])
        self.estado['campanha'] = self.gerar_campanha()
        self.aplicar_campanha_salva()
        self.salvar()

    def conquista(self, codigo):
        if codigo not in self.estado['conquistas']:
            self.estado['conquistas'].append(codigo)

    def tocar_objeto(self, objeto, resposta=None):
        """Retorna (mensagem, tipo). Tipo 'senha' solicita entrada ao jogador."""
        s = self.estado
        chave = self.sala['id'] + ':' + objeto['id']
        if chave not in s['vistos']:
            s['vistos'].append(chave)
            self.conquista('primeira_pista')
        texto = objeto['texto']
        if objeto.get('codigo'):
            if chave in s['resolvidos']:
                return ('Este mecanismo já foi desbloqueado.', 'ok')
            if resposta is None:
                return (texto, 'senha')
            if str(resposta).strip().upper() != objeto['codigo'].upper():
                s['tentativas'][chave] = s['tentativas'].get(chave, 0) + 1
                s['alerta'] = s.get('alerta', 0) + 1
                s['tempo_restante'] = max(0, s.get('tempo_restante', 0) - 60)
                restantes = 3 - s['tentativas'][chave]
                self.salvar()
                if s['tentativas'][chave] >= 3:
                    self.finalizar('Capturado pela mansão')
                    return ('O mecanismo dispara um alarme. Passos ecoam no andar de cima. A mansão percebeu sua presença: você foi capturado.', 'fim')
                return (f"O código está errado. Um ruído percorre os canos. Você perdeu 1 minuto e restam {restantes} tentativa(s).", 'erro')
            s['resolvidos'].append(chave)
            texto = objeto.get('sucesso', 'Mecanismo aberto!')
        if objeto.get('requer') and objeto['requer'] not in s['inventario']:
            self.salvar()
            return (texto + '\n\nVocê ainda precisa de: ' + objeto['requer'], 'erro')
        if objeto.get('item') and objeto['item'] not in s['inventario']:
            s['inventario'].append(objeto['item'])
            texto += '\n\n+ ITEM: ' + objeto['item']
            if len(s['inventario']) >= 4:
                self.conquista('colecionador')
        if objeto.get('avanca'):
            s['sala'] += 1
            texto += '\n\nA passagem se abre. Você avança para o próximo ambiente.'
            self.salvar()
            return (texto, 'avancar')
        if objeto.get('final'):
            self.salvar()
            return (texto, 'escolha')
        self.salvar()
        return (texto, 'ok')

    def dica(self):
        self.estado['dicas'] += 1
        self.estado['tempo_restante'] = max(0, self.estado.get('tempo_restante', 0) - 90)
        self.salvar()
        return 'Você força a memória a se concentrar. O relógio avança 1 minuto e 30 segundos.\n\n' + self.sala['pista']

    def finalizar(self, resultado):
        if self.estado['status'] != 'jogando':
            return
        if resultado in ('Fuga', 'Verdade revelada'):
            self.conquista('sobrevivente')
            if self.estado['dicas'] == 0:
                self.conquista('sem_pistas')
        if resultado == 'Verdade revelada':
            self.conquista('verdade')
        self.estado['status'] = 'finalizado'
        self.estado['resultado'] = resultado
        self.salvar()
        registro = dict(jogador=self.estado['jogador'], resultado=resultado,
                        salas_visitadas=self.estado['sala'] + 1,
                        itens=len(self.estado['inventario']), dicas=self.estado['dicas'],
                        alerta=self.estado.get('alerta', 0),
                        tempo_restante=self.estado['tempo_restante'],
                        conquistas=list(self.estado['conquistas']),
                        inicio=self.estado['inicio'], fim=datetime.now().isoformat(timespec='seconds'))
        self.historico.setdefault('partidas', []).append(registro)
        gravar('historico.json', self.historico)

    def escolha_final(self, revelar):
        if revelar and {'Diário completo', 'Prova da conspiração'}.issubset(self.estado['inventario']):
            self.finalizar('Verdade revelada')
        elif revelar:
            return 'Para revelar a verdade, você precisa do diário completo e da prova do porão.'
        else:
            self.finalizar('Fuga')
        return None


def modo_terminal():
    """Modo didático completo: input, while, for, if/elif/else e arquivos JSON."""
    jogo = Motor()
    print('\n=== O ÚLTIMO SEGREDO DA MANSÃO ===')
    while True:
        print('\n1 - Nova partida | 2 - Continuar | 3 - Histórico | 4 - Sair')
        opcao = input('Escolha: ').strip()
        if opcao == '1':
            nome = input('Nome do jogador: ').strip()
            if not nome:
                print('Digite um nome válido.')
                continue
            jogo.novo(nome)
        elif opcao == '2':
            if jogo.estado.get('status') != 'jogando':
                print('Nenhuma partida em andamento.')
                continue
        elif opcao == '3':
            for registro in jogo.historico.get('partidas', []):
                print(registro['jogador'], '-', registro['resultado'])
            continue
        elif opcao == '4':
            return
        else:
            print('Opção inválida.')
            continue
        while jogo.estado['status'] == 'jogando':
            sala = jogo.sala
            print('\n', sala['nome'], '\n', sala['descricao'])
            for numero, objeto in enumerate(sala['objetos'], 1):
                print(numero, '-', objeto['nome'])
            print('D - Dica | I - Inventário | S - Salvar e sair')
            acao = input('Sua ação: ').strip().lower()
            if acao == 's':
                jogo.salvar()
                break
            elif acao == 'i':
                print('Itens:', ', '.join(jogo.estado['inventario']) or 'Nenhum')
                continue
            elif acao == 'd':
                print(jogo.dica())
                continue
            elif acao.isdigit() and 1 <= int(acao) <= len(sala['objetos']):
                obj = sala['objetos'][int(acao) - 1]
                texto, tipo = jogo.tocar_objeto(obj)
                print(texto)
                if tipo == 'senha':
                    senha = input('Digite a senha: ')
                    texto, tipo = jogo.tocar_objeto(obj, senha)
                    print(texto)
                if tipo == 'escolha':
                    print('1 - Fugir | 2 - Revelar a verdade')
                    escolha = input('Decisão: ').strip()
                    aviso = jogo.escolha_final(escolha == '2')
                    if aviso:
                        print(aviso)
            else:
                print('Escolha inválida.')
        if jogo.estado['status'] == 'finalizado':
            print('\nFIM:', jogo.estado['resultado'])


class Interface:
    W, H = 1024, 700
    def __init__(self, raiz):
        self.raiz = raiz
        self.raiz.title('O Último Segredo da Mansão | Pixel Escape')
        self.raiz.geometry(f'{self.W}x{self.H}')
        self.raiz.minsize(self.W, self.H)
        self.jogo = Motor()
        self.fundo = '#10121c'
        self.painel = '#1c2131'
        self.texto = '#f3e6ce'
        self.ouro = '#e4bb77'
        self.canvas = tk.Canvas(raiz, width=self.W, height=self.H, bg=self.fundo,
                                highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)
        self.imagens = []
        self.alvos = []
        self.tela = 'menu'
        self.ultimo_tick = time.monotonic()
        self.som_ativo = True
        self.musica_rodando = False
        self.animacao_id = 0
        self.particulas = []
        self.hover_alvo = None
        self.timer_texto = None
        self.intro_pagina = 0
        self.raiz.bind('<Escape>', lambda e: self.menu())
        self.raiz.bind('<Return>', lambda e: self.proxima_intro() if self.tela == 'intro' else None)
        self.raiz.bind('<space>', lambda e: self.proxima_intro() if self.tela == 'intro' else None)
        self.raiz.bind('<F1>', lambda e: self.mostrar_dica() if self.tela == 'jogo' else None)
        self.raiz.bind('<F2>', lambda e: self.usar_lente() if self.tela == 'jogo' else None)
        self.raiz.bind('<i>', lambda e: self.inventario() if self.tela == 'jogo' else None)
        self.raiz.protocol('WM_DELETE_WINDOW', self.sair)
        self.menu()
        self.raiz.after(1000, self.tick)

    def musica(self):
        """Trilha ambiente original, reproduzida em loop no Windows."""
        if not self.som_ativo or self.musica_rodando or sys.platform != 'win32':
            return
        try:
            import winsound
            winsound.PlaySound(str(ASSETS / 'ambiente.wav'),
                               winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_LOOP)
            self.musica_rodando = True
        except RuntimeError:
            pass

    def som(self, nome):
        if not self.som_ativo:
            return
        caminho = ASSETS / (nome + '.wav')
        if sys.platform == 'win32' and caminho.exists():
            try:
                import winsound
                winsound.PlaySound(str(caminho), winsound.SND_FILENAME | winsound.SND_ASYNC)
                self.musica_rodando = False
                self.raiz.after(950, self.musica)
                return
            except RuntimeError:
                pass
        self.raiz.bell()

    def limpar(self):
        self.canvas.delete('all')
        self.imagens = []
        self.alvos = []

    def retangulo(self, x1, y1, x2, y2, cor, contorno=None):
        return self.canvas.create_rectangle(x1, y1, x2, y2, fill=cor,
                                            outline=contorno or cor, width=2)

    def texto_canvas(self, x, y, texto, tamanho=16, cor=None, largura=None, ancora='center'):
        return self.canvas.create_text(x, y, text=texto, fill=cor or self.texto,
                                       font=('Consolas', tamanho, 'bold'), width=largura,
                                       anchor=ancora, justify='center')

    def botao(self, x, y, largura, titulo, comando, cor='#171b2b'):
        # Botões com moldura dupla, sombra e acento luminoso em dourado.
        self.retangulo(x+3, y+4, x+largura+3, y+46, '#090b14', '#090b14')
        self.retangulo(x, y, x+largura, y+42, cor, '#8d633d')
        self.retangulo(x+3, y+3, x+largura-3, y+39, cor, '#d5a45d')
        self.texto_canvas(x+largura//2, y+21, titulo, 11, '#f4d49a')
        self.alvos.append(((x,y,x+largura,y+42), comando))

    def registrar_cliques(self):
        self.canvas.bind('<Button-1>', self.clique)
        self.canvas.config(cursor='hand2')

    def clique(self, evento):
        for alvo in reversed(self.alvos):
            (x1, y1, x2, y2), funcao = alvo[0], alvo[1]
            if x1 <= evento.x <= x2 and y1 <= evento.y <= y2:
                funcao()
                return

    def imagem(self, nome, x, y):
        caminho = ASSETS / (nome + '.png')
        if caminho.exists():
            foto = tk.PhotoImage(file=str(caminho))
            self.imagens.append(foto)
            self.canvas.create_image(x, y, image=foto, anchor='nw')

    def menu(self):
        self.tela = 'menu'
        self.musica()
        self.limpar()
        self.retangulo(0, 0, 1024, 700, '#080b16')
        self.imagem('capa', 0, 0)
        # Layout dividido: painel editorial à esquerda e cenário respirando à direita.
        self.retangulo(0, 0, 438, 700, '#0b101d', '#8d633d')
        self.retangulo(14, 14, 424, 686, '#111827', '#493b37')
        self.texto_canvas(219, 92, 'O ÚLTIMO', 29, '#f0c47e')
        self.texto_canvas(219, 132, 'SEGREDO DA', 25, '#f0c47e')
        self.texto_canvas(219, 170, 'MANSÃO', 33, '#f0c47e')
        self.retangulo(75, 198, 363, 200, '#c18a4c')
        self.texto_canvas(219, 226, 'ARQUIVO DE INVESTIGAÇÃO', 9, '#a9b5c8')
        self.texto_canvas(219, 250, 'Cada partida revela um caso diferente.', 10, '#e8e0d2')
        self.botao(73, 290, 292, 'NOVA INVESTIGAÇÃO', self.nova)
        if self.jogo.estado.get('status') == 'jogando':
            self.botao(73, 340, 292, 'RETOMAR INVESTIGAÇÃO', self.jogar)
        else:
            self.botao(73, 340, 292, 'COMO JOGAR', self.ajuda)
        self.botao(73, 390, 140, 'HISTÓRICO', self.historico)
        self.botao(225, 390, 140, 'CONQUISTAS', self.conquistas)
        self.botao(73, 440, 292, 'ÁUDIO: ' + ('ATIVO' if self.som_ativo else 'MUDO'), self.alternar_som)
        self.texto_canvas(219, 535, 'E  INVESTIGAR', 10, '#a9b5c8')
        self.texto_canvas(219, 558, 'I  INVENTÁRIO  •  F2  LENTE', 10, '#a9b5c8')
        self.texto_canvas(219, 635, 'A CASA LEMBRA DE TUDO.', 10, '#c18a4c')
        self.registrar_cliques()

    def alternar_som(self):
        self.som_ativo = not self.som_ativo
        if not self.som_ativo and sys.platform == 'win32':
            try:
                import winsound
                winsound.PlaySound(None, 0)
            except RuntimeError:
                pass
            self.musica_rodando = False
        self.menu()

    def nova(self):
        if self.jogo.estado.get('status') == 'jogando':
            if not messagebox.askyesno('Nova partida', 'Substituir o progresso atual?'):
                return
        nome = simpledialog.askstring('Jogador', 'Qual é o seu nome?', parent=self.raiz)
        if nome and nome.strip():
            self.jogo.novo(nome.strip()[:25])
            self.intro_pagina = 0
            self.mostrar_intro()

    def mostrar_intro(self):
        """Abertura narrativa em três quadros, com texto progressivo."""
        self.tela = 'intro'
        self.limpar()
        self.imagem('capa', 0, 0)
        self.retangulo(70, 72, 954, 625, '#111522', '#b88a57')
        paginas = [
            (
                "23 DE OUTUBRO DE 1987  •  23:47",
                "A chuva cobre a estrada quando você encontra uma carta presa ao portão. "
                "O envelope traz apenas seu nome e o selo da família Valença."
            ),
            (
                "A ÚLTIMA CARTA",
                "“Se está lendo isto, não deixe que a casa chegue à meia-noite. "
                "O diário está na biblioteca. A verdade está enterrada no porão. "
                "Não confie no retrato da sala.”"
            ),
            (
                "A PORTA SE FECHA",
                "Você entra para procurar respostas. A porta bate sozinha. "
                "Um relógio antigo começa a funcionar: faltam 25 minutos para meia-noite. "
                "A mansão parece estar observando cada movimento seu."
            )
        ]
        titulo, corpo = paginas[self.intro_pagina]
        self.texto_canvas(512, 145, 'O ÚLTIMO SEGREDO DA MANSÃO', 24, self.ouro)
        self.texto_canvas(512, 235, titulo, 17, '#f0c77e')
        self.intro_texto_id = self.canvas.create_text(
            150, 295, text='', fill=self.texto, width=720, anchor='nw',
            font=('Consolas', 15, 'bold')
        )
        self.intro_corpo = corpo
        self.intro_pos = 0
        self.animar_texto_intro()
        self.botao(375, 535, 274, 'PULAR / CONTINUAR', self.proxima_intro)
        self.registrar_cliques()

    def animar_texto_intro(self):
        if self.tela != 'intro':
            return
        self.intro_pos = min(len(self.intro_corpo), self.intro_pos + 3)
        self.canvas.itemconfigure(self.intro_texto_id, text=self.intro_corpo[:self.intro_pos])
        if self.intro_pos < len(self.intro_corpo):
            self.raiz.after(28, self.animar_texto_intro)

    def proxima_intro(self):
        if self.intro_pos < len(self.intro_corpo):
            self.intro_pos = len(self.intro_corpo)
            self.canvas.itemconfigure(self.intro_texto_id, text=self.intro_corpo)
            return
        self.intro_pagina += 1
        if self.intro_pagina < 3:
            self.mostrar_intro()
        else:
            self.som('porta')
            self.jogar()

    def iniciar_ambiente_animado(self):
        """Partículas de poeira e brilho pulsante sobre a cena pixel art."""
        self.particulas = []
        import random
        for _ in range(24):
            self.particulas.append({
                'x': random.randint(25, 995),
                'y': random.randint(75, 510),
                'vel': random.choice([0.35, 0.55, 0.8]),
                'fase': random.randint(0, 20)
            })
        self.animar_ambiente()

    def animar_ambiente(self):
        if self.tela != 'jogo':
            return
        self.canvas.delete('ambiente_animado')
        # Poeira suspensa: pequenos pixels que flutuam lentamente.
        for p in self.particulas:
            p['y'] -= p['vel']
            p['x'] += 0.25 if p['fase'] % 2 else -0.2
            p['fase'] += 1
            if p['y'] < 75:
                p['y'] = 510
            if p['x'] < 20:
                p['x'] = 1000
            if p['x'] > 1000:
                p['x'] = 20
            brilho = '#9b8060' if p['fase'] % 3 else '#d8b77d'
            self.canvas.create_rectangle(
                int(p['x']), int(p['y']), int(p['x']) + 2, int(p['y']) + 2,
                fill=brilho, outline=brilho, tags='ambiente_animado'
            )
        # Mantém a iluminação estável; apenas a poeira se movimenta.
        self.raiz.after(90, self.animar_ambiente)

    def atualizar_hover(self, evento):
        if self.tela != 'jogo':
            return
        alvo = None
        for registro in reversed(self.alvos):
            if len(registro) != 3:
                continue
            caixa, funcao, objeto = registro
            x1, y1, x2, y2 = caixa
            if x1 <= evento.x <= x2 and y1 <= evento.y <= y2:
                alvo = objeto['id']
                break
        self.canvas.delete('hover_fx')
        if alvo != self.hover_alvo:
            self.hover_alvo = alvo
            self.canvas.config(cursor='hand2' if alvo else 'arrow')
        if alvo:
            for registro in reversed(self.alvos):
                if len(registro) != 3 or registro[2]['id'] != alvo:
                    continue
                caixa = registro[0]
                x1, y1, x2, y2 = caixa
                self.canvas.create_rectangle(x1, y1, x2, y2, outline='#f4c77b',
                                             width=2, dash=(5, 3), tags='hover_fx')
                self.canvas.create_rectangle(x1+4, y1+4, x2-4, y2-4,
                                             outline='#53d7ce', width=1, tags='hover_fx')
                self.canvas.create_text((x1+x2)//2, max(75,y1-12),
                                        text='✦ EXAMINAR', fill='#f4c77b',
                                        font=('Consolas', 9, 'bold'), tags='hover_fx')
                break

    def jogar(self):
        if self.jogo.estado.get('status') != 'jogando':
            self.menu()
            return
        self.tela = 'jogo'
        self.musica()
        self.limpar()
        sala = self.jogo.sala
        self.imagem(sala['id'], 0, 0)
        self.retangulo(0, 0, 1024, 64, '#090d19', '#4d3b34')
        self.retangulo(0, 61, 1024, 64, '#c18a4c')
        self.texto_canvas(22, 18, 'O ÚLTIMO SEGREDO', 10, '#e0b66f', ancora='nw')
        self.texto_canvas(22, 40, sala['nome'], 14, '#f4e4c8', ancora='nw')
        self.texto_canvas(505, 29, f"ALERTA  {self.jogo.estado.get('alerta', 0)}", 11, '#ef8a83')
        self.botao(575, 10, 112, 'LENTE [F2]', self.usar_lente)
        segundos = max(0, self.jogo.estado['tempo_restante'])
        self.timer_texto = self.texto_canvas(
            1000, 29, f'{segundos//60:02}:{segundos%60:02}', 17,
            '#ff9990' if segundos < 180 else '#f4d49a', ancora='ne'
        )
        self.retangulo(0, 528, 1024, 700, '#090d19', '#7d593d')
        self.retangulo(0, 528, 1024, 532, '#d3a15d')
        self.texto_canvas(28, 550, 'DIÁRIO DE CAMPO  /  OBJETIVO ATUAL', 9, '#cda36d', ancora='nw')
        self.texto_canvas(28, 570, sala['descricao'], 12, '#eee1cb', 920, 'nw')
        self.texto_canvas(28, 610, 'E  EXAMINAR     I  INVENTÁRIO     F1  PISTA     F2  LENTE', 9, '#a8b4c7', ancora='nw')
        self.botao(28, 645, 174, 'INVENTÁRIO [I]', self.inventario)
        self.botao(220, 645, 174, 'PISTA [F1]', self.mostrar_dica)
        self.botao(412, 645, 174, 'SALVAR', self.salvar)
        self.botao(604, 645, 174, 'ARQUIVO', self.conquistas)
        self.botao(796, 645, 198, 'MENU [ESC]', self.menu)
        for objeto in sala['objetos']:
            x1,y1,x2,y2 = objeto['pos']
            # As coordenadas são relativas à imagem 640x360, exibida em 960x450.
            a,b,c,d = 32+int(x1*1.5), 72+int(y1*1.25), 32+int(x2*1.5), 72+int(y2*1.25)
            # A área clicável fica invisível; o jogador só vê a arte do cenário.
            self.alvos.append(((a,b,c,d), lambda o=objeto: self.investigar(o), objeto))
            # Pequeno marcador de investigação; não cobre a arte do cenário.
            self.canvas.create_text(c-8, b+8, text='✦', fill='#f0bd69',
                                    font=('Consolas', 13, 'bold'))
        self.registrar_cliques()
        self.canvas.bind('<Motion>', self.atualizar_hover)
        self.iniciar_ambiente_animado()

    def investigar(self, objeto):
        mensagem, tipo = self.jogo.tocar_objeto(objeto)
        if tipo == 'senha':
            self.abrir_mecanismo(objeto)
            return
        self.concluir_interacao(objeto, mensagem, tipo)

    def abrir_mecanismo(self, objeto):
        """Abre um painel tátil de discos numéricos ou alfabéticos."""
        self.tela = 'mecanismo'
        self.mecanismo_objeto = objeto
        codigo = str(objeto.get('codigo', ''))
        self.mecanismo_valores = [0 if ch.isdigit() else 'A' for ch in codigo]
        self.mecanismo_tamanho = len(codigo)
        sala_id = self.jogo.sala['id']
        indice = {'biblioteca': 0, 'escritorio': 1, 'porao': 2}.get(sala_id, 0)
        self.mecanismo_tipo = self.jogo.estado.get('campanha', {}).get('tipos', ['discos']*3)[indice]
        self.mecanismo_sequencia = ''
        self.desenhar_mecanismo()

    def desenhar_mecanismo(self):
        self.limpar()
        self.imagem('capa', 0, 0)
        self.retangulo(95, 82, 929, 618, '#171a29', self.ouro)
        self.texto_canvas(512, 126, 'MECANISMO DE PRECISÃO', 23, self.ouro)
        self.texto_canvas(512, 165, self.mecanismo_objeto['nome'].upper(), 14)
        instrucao = {'discos': 'Gire os discos até formar a combinação.', 'teclado': 'Selecione os caracteres na ordem das pistas.', 'sequencia': 'Repita a sequência encontrada nas pistas.'}[self.mecanismo_tipo]
        self.texto_canvas(512, 204, instrucao, 11, self.texto)
        if self.mecanismo_tipo in ('teclado', 'sequencia'):
            self.texto_canvas(512, 247, self.mecanismo_sequencia or '·  ·  ·  ·', 22, self.ouro)
            chars = '0123456789' if self.mecanismo_objeto.get('codigo', '').isdigit() else 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
            for i, char in enumerate(chars):
                linha, coluna = divmod(i, 10)
                x, y = 222 + coluna * 64, 305 + linha * 57
                if y < 465:
                    self.botao(x, y, 54, char, lambda ch=char: self.adicionar_caractere(ch))
            self.botao(300, 505, 190, 'APAGAR', self.apagar_sequencia)
            self.botao(520, 505, 190, 'TESTAR', self.testar_mecanismo)
            self.registrar_cliques()
            return
        n = self.mecanismo_tamanho
        espacamento = min(150, 620 // n)
        inicio = 512 - (n - 1) * espacamento // 2
        for i, valor in enumerate(self.mecanismo_valores):
            x = inicio + i * espacamento
            self.retangulo(x-42, 272, x+42, 390, '#303747', '#b88a57')
            self.texto_canvas(x, 328, str(valor), 30, self.ouro)
            self.botao(x-35, 230, 70, '▲', lambda k=i: self.girar_disco(k, 1))
            self.botao(x-35, 400, 70, '▼', lambda k=i: self.girar_disco(k, -1))
        self.texto_canvas(512, 455, 'A combinação correta libera o compartimento.', 12)
        self.botao(300, 505, 190, 'TESTAR', self.testar_mecanismo)
        self.botao(520, 505, 190, 'VOLTAR', self.jogar)
        self.registrar_cliques()

    def adicionar_caractere(self, char):
        if len(self.mecanismo_sequencia) < self.mecanismo_tamanho:
            self.mecanismo_sequencia += char
            self.desenhar_mecanismo()

    def apagar_sequencia(self):
        self.mecanismo_sequencia = self.mecanismo_sequencia[:-1]
        self.desenhar_mecanismo()

    def girar_disco(self, indice, sentido):
        valor = self.mecanismo_valores[indice]
        if isinstance(valor, int):
            self.mecanismo_valores[indice] = (valor + sentido) % 10
        else:
            alfabeto = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
            pos = (alfabeto.index(valor) + sentido) % len(alfabeto)
            self.mecanismo_valores[indice] = alfabeto[pos]
        self.som('acerto')
        self.desenhar_mecanismo()

    def testar_mecanismo(self):
        resposta = self.mecanismo_sequencia if self.mecanismo_tipo in ('teclado', 'sequencia') else ''.join(str(v) for v in self.mecanismo_valores)
        mensagem, tipo = self.jogo.tocar_objeto(self.mecanismo_objeto, resposta)
        if tipo == 'erro':
            self.som('erro')
            messagebox.showwarning('Combinação incorreta', mensagem)
            self.desenhar_mecanismo()
            return
        self.concluir_interacao(self.mecanismo_objeto, mensagem, tipo)

    def concluir_interacao(self, objeto, mensagem, tipo):
        if tipo == 'erro':
            self.som('erro')
        else:
            self.som('acerto')
        if tipo == 'escolha':
            self.escolha_final()
            return
        if tipo == 'fim':
            messagebox.showerror('Fim de jogo', mensagem)
            self.resultado()
            return
        messagebox.showinfo(objeto['nome'], mensagem)
        if tipo == 'avancar':
            self.som('porta')
        self.jogar()

    def escolha_final(self):
        revelar = messagebox.askyesno('A decisão final',
            'O portão está aberto.\n\nSIM: revelar a conspiração.\nNÃO: fugir imediatamente.')
        aviso = self.jogo.escolha_final(revelar)
        if aviso:
            messagebox.showwarning('Evidências insuficientes', aviso)
            self.jogar()
        else:
            self.resultado()

    def resultado(self):
        self.tela = 'resultado'
        self.limpar()
        self.imagem('capa', 0, 0)
        self.retangulo(160, 165, 864, 515, '#171a29', self.ouro)
        resultado = self.jogo.estado.get('resultado', 'Fim')
        self.texto_canvas(512, 232, resultado.upper(), 28, self.ouro)
        self.texto_canvas(512, 310, f"JOGADOR: {self.jogo.estado.get('jogador', '')}", 15)
        self.texto_canvas(512, 351, f"ITENS: {len(self.jogo.estado['inventario'])}   •   PISTAS: {self.jogo.estado['dicas']}", 14)
        self.botao(377, 415, 270, 'VOLTAR AO MENU', self.menu)
        self.registrar_cliques()

    def painel_texto(self, titulo, linhas):
        self.tela = 'painel'
        self.limpar()
        self.imagem('capa', 0, 0)
        self.retangulo(95, 82, 929, 618, '#171a29', self.ouro)
        self.texto_canvas(512, 128, titulo, 24, self.ouro)
        for i, linha in enumerate(linhas[:13]):
            self.texto_canvas(133, 181+i*29, linha, 12, self.texto, 760, 'nw')
        self.botao(400, 557, 224, 'VOLTAR', self.jogar if self.jogo.estado.get('status') == 'jogando' else self.menu)
        self.registrar_cliques()

    def inventario(self):
        itens = self.jogo.estado.get('inventario', [])
        self.painel_texto('INVENTÁRIO', ['• ' + item for item in itens] or ['Seu inventário está vazio.'])

    def usar_lente(self):
        campanha = self.jogo.estado.get('campanha', {})
        sala = self.jogo.sala['id']
        pistas = {
            'hall': f"A lente revela uma inscrição quase apagada: {campanha.get('ano', '1987')} não é uma data comemorativa. É o dia do desaparecimento.",
            'biblioteca': "Sob a tinta do globo há marcas de pressão. Compare as posições com as anotações do livro; a ordem importa mais que os números.",
            'escritorio': "A lente revela pequenos riscos no mostrador. Os ponteiros foram movidos para esconder a ordem dos sinos.",
            'porao': f"Na cera, a lente mostra marcas de raspagem. As letras {campanha.get('codigo_painel', 'LUZ')} devem ser lidas na direção indicada pela chama.",
            'camara': f"A lente revela o selo {campanha.get('selo', 'corvo')} repetido atrás do altar. A mesma marca aparece no primeiro documento."
        }
        self.jogo.estado['tempo_restante'] = max(0, self.jogo.estado.get('tempo_restante', 0) - 30)
        self.jogo.estado['lente_usos'] = self.jogo.estado.get('lente_usos', 0) + 1
        self.jogo.salvar()
        self.som('acerto')
        messagebox.showinfo('Lente de investigação', pistas.get(sala, 'A lente revela marcas escondidas na superfície.'))
        self.jogar()

    def mostrar_dica(self):
        dica = self.jogo.dica()
        self.som('acerto')
        messagebox.showinfo('Pista encontrada', dica)
        self.jogar()

    def salvar(self):
        self.jogo.salvar()
        messagebox.showinfo('Salvo', 'Progresso salvo em dados/progresso.json.')

    def historico(self):
        registros = self.jogo.historico.get('partidas', [])
        linhas = [f"{p['jogador']}  |  {p['resultado']}  |  {p['itens']} itens  |  {p['dicas']} pistas"
                  for p in reversed(registros[-13:])]
        self.painel_texto('HISTÓRICO DE PARTIDAS', linhas or ['Ainda não há partidas concluídas.'])

    def conquistas(self):
        desbloqueadas = set(self.jogo.estado.get('conquistas', []))
        linhas = [('[X] ' if c['id'] in desbloqueadas else '[ ] ') + c['nome'] + ' — ' + c['descricao']
                  for c in self.jogo.dados['conquistas']]
        self.painel_texto('CONQUISTAS', linhas)

    def ajuda(self):
        self.painel_texto('COMO JOGAR', [
            'Investigue os objetos destacados com o mouse.',
            'Colete itens para abrir portas e mecanismos.',
            'Observe cartas, retratos e inscrições para descobrir senhas.',
            'F1: pedir pista   |   I: inventário   |   ESC: menu',
            'Você tem 20 minutos e apenas três tentativas por código.',
            'Erros custam 1 minuto; pedir uma dica custa 1 minuto e 30 segundos.',
            'O progresso é salvo em JSON e pode ser recuperado depois.',
            'Na última sala, escolha fugir ou revelar a verdade.',
            'Modo didático no terminal: python main.py --terminal'
        ])

    def tick(self):
        agora = time.monotonic()
        intervalo = agora - self.ultimo_tick
        self.ultimo_tick = agora
        if self.tela in ('jogo', 'mecanismo') and self.jogo.estado.get('status') == 'jogando':
            self.jogo.estado['tempo_restante'] = max(0, self.jogo.estado['tempo_restante'] - int(intervalo + 0.5))
            if self.jogo.estado['tempo_restante'] <= 0:
                self.jogo.finalizar('Tempo esgotado')
                self.som('erro')
                self.resultado()
            else:
                self.jogo.salvar()
                if self.tela == 'jogo' and self.timer_texto is not None:
                    segundos = int(self.jogo.estado['tempo_restante'])
                    self.canvas.itemconfigure(
                        self.timer_texto,
                        text=f'TEMPO {segundos//60:02}:{segundos%60:02}',
                        fill='#ff9990' if segundos < 180 else self.texto
                    )
        self.raiz.after(1000, self.tick)

    def sair(self):
        if self.jogo.estado.get('status') == 'jogando':
            self.jogo.salvar()
        self.raiz.destroy()


if __name__ == '__main__':
    if '--terminal' in sys.argv:
        modo_terminal()
    else:
        janela = tk.Tk()
        Interface(janela)
        janela.mainloop()
