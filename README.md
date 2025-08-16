# Space Defender - Futuristic Edition

![Space Defender](https://img.shields.io/badge/Version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/Python-3.13+-green.svg)
![Pygame](https://img.shields.io/badge/Pygame-2.6.1-red.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

Um jogo de nave espacial futurista com sistema de waves, power-ups e múltiplas armas. Defenda a Terra de ondas de asteroides enquanto coleta power-ups para aumentar seu poder de fogo!

## 📸 Screenshots

![Tela Inicial](https://via.placeholder.com/800x600?text=Tela+Inicial+Space+Defender)
![Gameplay](https://via.placeholder.com/800x600?text=Gameplay+Space+Defender)
![Game Over](https://via.placeholder.com/800x600?text=Game+Over+Space+Defender)

## 🎮 Gameplay

### Objetivo
- Sobreviva ao máximo possível destruindo asteroides
- Colete power-ups para mudar sua arma
- Alcance a maior pontuação e wave possível

### Controles
| Tecla | Ação |
|-------|------|
| `← →` | Mover a nave para esquerda/direita |
| `Espaço` | Atirar |
| `Enter` | Começar o jogo / Reiniciar após game over |
| `Mouse` | Interagir com botões na tela de game over |

### Mecânicas Principais

#### 🌊 Sistema de Waves
- **Wave 1-3**: Apenas asteroides pequenos
- **Wave 4-6**: Asteroides pequenos e médios
- **Wave 7+**: Asteroides pequenos, médios e grandes
- A dificuldade aumenta progressivamente

#### 🔫 Sistema de Armas
O jogo conta com 5 armas diferentes, cada uma com características únicas:

1. **BASIC (Ciano)**
   - Tiro único padrão
   - Cooldown: 10 frames
   - Dano: 1

2. **SPREAD (Amarela)**
   - Dispara 3 tiros em formação de leque
   - Cooldown: 15 frames
   - Dano: 1 por tiro
   - Ideal para múltiplos alvos

3. **RAPID (Verde Neon)**
   - Tiros muito rápidos
   - Cooldown: 3 frames
   - Dano: 1
   - Permite spam de tiros

4. **LASER BEAM (Roxa)**
   - Laser contínuo com efeito de brilho
   - Cooldown: 8 frames
   - Dano: 1
   - Visual impressionante

5. **HOMING (Rosa)**
   - Mísseis teleguiados que perseguem asteroides
   - Cooldown: 20 frames
   - Dano: 1
   - Ataca automaticamente o asteroide mais próximo

#### ⚡ Power-ups
- Aparecem a cada 15 segundos
- Duram 10 segundos cada
- Mudam temporariamente sua arma
- Cada power-up tem um ícone colorido representando sua arma

#### 🛡️ Sistema de Saúde e Vidas
- **Vidas**: Você começa com 3 vidas
- **Saúde**: Barra de saúde que regenera lentamente
- **Escudo**: Fica ativo por 2 segundos após receber dano
- **Invulnerabilidade**: Período de 2 segundos após ser atingido

## 🚀 Instalação

### Pré-requisitos
- Python 3.13 ou superior
- Pip (gerenciador de pacotes do Python)

### Passos
1. Clone o repositório:
   
git clone (https://github.com/gaog-dev/Space-Defender)
cd space-defender

2. Instale as dependências:
   pip install pygame numpy

3. Execute o jogo:
   python space_defender_final.py

4. Testes
O jogo inclui testes unitários para garantir o funcionamento correto das principais mecânicas:
python -m unittest space_defender_final.py

Testes Implementados
test_bullet_creation(): Verifica se as balas são criadas corretamente
test_player_shoot_basic(): Testa o tiro com a arma básica
test_player_shoot_spread(): Testa o tiro com a arma spread
test_wave_manager(): Verifica o funcionamento do sistema de waves
test_asteroid_health(): Testa a saúde dos asteroides

# 📁 Estrutura do Projeto

 ### space-defender/
 ### ├── space_defender_final.py  # Código principal do jogo
 ### ├── README.md                # Este arquivo
 ### └── assets/                  # Pasta para assets (imagens, sons, etc.)
  #### ├── images/
  #### ├── sounds/
  #### └── fonts/
    
# 🔧 Personalização
### Ajustar Dificuldade
No arquivo space_defender_final.py, você pode modificar:

### No construtor de WaveManager:
self.asteroids_in_wave = 3  # Número inicial de asteroides
self.spawn_delay = 0.5       # Tempo entre spawns

### No método update() de Player:
self.speed_x = 12           # Velocidade da nave

### No spawn de power-ups:
if powerup_spawn_timer > 15.0:  # Tempo entre power-ups

Adicionar Novas Armas
  1. Adicione um novo valor ao enum WeaponType
  2. Implemente a lógica de tiro na classe Player
  3. Adicione o visual correspondente na classe Bullet
  4. Crie o ícone do power-up na classe PowerUp
     
Modificar Cores
As cores estão definidas no início do arquivo:
# Cores Futuristas
CYAN = (0, 255, 255)
ELECTRIC_BLUE = (0, 170, 255)
NEON_GREEN = (57, 255, 20)
### ... e outras

### 🐛 Problemas Conhecidos
PROBLEMA
SOLUÇÃO
Erro AttributeError: 'Player' object has no attribute 'weapon_type'	
Certifique-se de que todos os atributos são inicializados antes de serem usados nos métodos de desenho
Erro AttributeError: 'PowerUp' object has no attribute 'colors'	
Verifique se o dicionário colors é inicializado antes de draw_powerup()
Testes falhando	
Ajuste os valores de dt nos testes para corresponderem aos valores usados no jogo
Não consegue atirar	
Verifique se a lista bullets está sendo mantida entre os frames

### 🤝 Contribuição
Contribuições são bem-vindas! Por favor, siga estas etapas:

Faça um fork do projeto
Crie uma branch para sua feature (git checkout -b feature/nova-feature)
Commit suas mudanças (git commit -am 'Adiciona nova feature')
Push para a branch (git push origin feature/nova-feature)
Abra um Pull Request

### 📄 Licença
Este projeto está licenciado sob a Licença MIT - veja o arquivo LICENSE para detalhes.

# 👨‍💻 Desenvolvedores
Guilherme Oliveira - Desenvolvedor Principal

# 🙏 Agradecimentos
À comunidade Pygame pelos excelentes recursos
A todos os testadores que ajudaram a identificar bugs
À comunidade de código aberto pelas inspirações

# 📞 Contato
Guilherme Oliveira - @seu-twitter - gaoliveira2077@gmail.com

Space Defender - Futuristic Edition © 2024. Todos os direitos reservados.
