from scsr.models.elements import ElementAO, ElementReferenceAO

def create_element(enName,ptName,ref):
    el=ElementAO()
    el.add_name('en',enName)
    el.add_name('pt',ptName)
    el.save()# TODO: Create the ElementReference representation and code the reference adding here.
    er=ElementReferenceAO.get_reference(el)
    er.set_reference(ref)
    er.save()

def start_ontology():
    
    create_element("Multiple Entity Manipulation","Manipulação de Múltiplas Entidades",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/Multiple_Entity_Manipulation"})
    create_element("Single Entity Manipulation","Manipulação de Entidade Individual",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/Single_Entity_Manipulation"})
    create_element("Direct Manipulation","Manipulação Direta",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/Manipulation_Method"})
    create_element("Indirect Manipulation","Manipulação Indireta",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/Indirect_Manipulation"})
    create_element("Digital Push Button","Botão Digital",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/Digital_Pushbutton"})
    create_element("Analog Push Button","Botão Analógico",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/Analog_Pushbutton"})
    create_element("Directional Pad","JoyPad",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/Direction_Pad"})
    create_element("Joystick","Joystick",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/Fourway_Joystick"})
    create_element("Thruster","Alavanca",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/Thruster_(two-way)_Joystick"})
    create_element("Paddle","Paddle",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/Rotary_Paddle_Control"})
    create_element("Accelerometer","Acelerômetro",
        {"type":"single", "source":"text", "ref":"Technological Device"})
    create_element("Magnetometer","Magnetômetro",
        {"type":"single", "source":"text", "ref":"Technological Device"})
    create_element("Microphone","Microfone",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/Microphone"})
    create_element("Altimeter","Altímetro",
        {"type":"single", "source":"text", "ref":"Technological Device"})
    create_element("Camera Recognition","Reconhecimento por Câmera",
        {"type":"single", "source":"text", "ref":"Technological Algorithm"})
    create_element("Lightgun","Pistola",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/Lightgun"})
    create_element("GPS","GPS",
        {"type":"single", "source":"text", "ref":"Technological Device"})
    create_element("Touch Screen","Tela de Toque",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/Touch-Sensitive_Screen"})
    create_element("Stylus Pen","Caneta Stylus",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/Stylus_Pen"})
    create_element("1D Gameworld","Mundo 1D",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/1-Dimensional_Gameworld"})
    create_element("2D Gameworld","Mundo 2D",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/2-Dimensional_Gameworld"})
    create_element("3D Gameworld","Mundo 3D",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/3-Dimensional_Gameworld"})
    create_element("Undefined Gameworld Cardinality","Cardinalidade de Mundo Indefinida",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/Undefined_Gameworld_Cardinality"})
    create_element("Audio","Áudio",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/Audio_Display_Hardware"})
    create_element("Haptic Device","Dispositivo Háptico",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/Haptic_Display"})
    create_element("Monitor","Monitor",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/Video_Monitor"})
    create_element("VR Goggles","Óculos VR",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/VR_Goggles"})
    create_element("Closed Cycle Haptic","Háptico de Circuito Fechado",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/Closed_Cycle_Haptics"})
    create_element("Open Cycle Haptic","Háptico de Circuito Aberto",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/Open_Cycle_Haptics"})
    create_element("Warning Feedback","Resposta de Alerta",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/Warning"})
    create_element("Confirmation Feedback","Resposta de Confirmação",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/Confirmation"})
    create_element("First Person View","Visão em Primeira Pessoa",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/First-person_Point_of_View"})
    create_element("Third Person View","Visão em Terceira Pessoa",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/Third-person_Point_of_View"})
    create_element("Second Person View","Visão em Segunda Pessoa",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/Second-person_Point_of_View"})
    create_element("Located Camera","Câmera Fixa",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/Located_Camera"})
    create_element("Roaming Camera","Câmera Livre",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/Roaming_Camera"})
    create_element("Targeted Camera","Câmera com Alvo",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/Targeted_Camera"})
    create_element("3D Camera Movement","Movimentação 3D da Câmera",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/Three_Dimensional_Camera_Motion"})
    create_element("2D Camera Movement","Movimentação 2D da câmera",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/Two_Dimensional_Camera_Motion"})
    create_element("3D Frame","Quadro 3D",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/Three_Dimensional_Frame"})
    create_element("2D Frame","Quadro 2D",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/Two_Dimensional_Frame"})
    create_element("Buttonpress Indicator","Indicador de Botão Pressionado",
        {"type":"single","source":"link","ref":"http://www.gameontology.com/index.php/Buttonpress_Indicator"})
    create_element("Control Bindings Display","Exibição de Atribuição a Comando",
        {"type":"single","source":"link","ref":"http://www.gameontology.com/index.php/Control_Bindings_Display"})
    create_element("Health Indicator","",
        {"type":"single","source":"link","ref":"http://www.gameontology.com/index.php/Health_Indicator"})
    create_element("Lives Indicator","",
        {"type":"single","source":"link","ref":"http://www.gameontology.com/index.php/Lives_Indicator"})
    create_element("Map Display","",
        {"type":"single","source":"link","ref":"http://www.gameontology.com/index.php/Map_Display"})
    create_element("Next Piece Indicator","",
        {"type":"single","source":"link","ref":"http://www.gameontology.com/index.php/Next_Piece_Indicator"})
    create_element("Player Configurable Buttons/Keys","",
        {"type":"single","source":"link","ref":"http://www.gameontology.com/index.php/Player_Configurable_Buttons/Keys"})
    create_element("Points Indicator","",
        {"type":"single","source":"link","ref":"http://www.gameontology.com/index.php/Points_Indicator"})
    create_element("Radar Display","",
        {"type":"single","source":"link","ref":"http://www.gameontology.com/index.php/Radar_Display"})
    create_element("Special Weapon Indicator","",
        {"type":"single","source":"link","ref":"http://www.gameontology.com/index.php/Special_Weapon_Indicator"})
    create_element("Time Indicator","",
        {"type":"single","source":"link","ref":"http://www.gameontology.com/index.php/Time_Indicator"})
    create_element("Vehicular Instrumentation","",
        {"type":"single","source":"link","ref":"http://www.gameontology.com/index.php/Vehicular_Instrumentation"})
    create_element("Complete Information","Informação Completa",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/Complete_Information"})
    create_element("Dominant Strategy","Estratégia Dominante",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/Dominant_Strategy"})
    create_element("Economies of Scale","Economia de Escala",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/Economies_of_Scale"})
    create_element("Economies of Scope","Economia de Escopo",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/Economies_of_Scope"})
    create_element("Inconplete Information","Informação Incompleta",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/Incomplete_Information"})
    create_element("Intransitive Relationships","Relações Intransitivas",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/Intransitive_Relationships"})
    create_element("Transitive Relationships","Relações Transitivas",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/Transitive_Relationships"})
    create_element("0-Dimensional Gameplay","Jogabilidade Adimensional",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/0-Dimension_Gameplay"})
    create_element("1-Dimensional Gameplay","Jogabilidade Unidimensional",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/1-Dimensional_Gameplay"})
    create_element("2-Dimensional Gameplay","Jogabilidade Bidimensional",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/2-Dimensional_Gameplay"})
    create_element("3-Dimensional Gameplay","Jogabilidade Tridimensional",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/3-Dimensional_Gameplay"})
    create_element("Undefined Cardinality of Gameplay","Cardinalidade Indefinida de Jogabilidade",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/Undefined_Cardinality_of_Gameplay"})
    create_element("Evaluation of Ending","Avaliação de Término de Jogo",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/Evaluation_of_Ending"})
    create_element("Gameworld Exhaustion","Exaustão do Mundo de Jogo",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/Gameworld_Exhaustion"})
    create_element("Narrative Exhaustion","Exaustão da Narrativa",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/Narrative_Exhaustion"})
    create_element("Resource Exhaustion","Exaustão de Recursos",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/Resource_Exhaustion"})
    create_element("Cooperative Multiplayer","Multijogadores Coperativo",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/Cooperative_Multiplayer"})
    create_element("Competitive Multiplayer","Multijogadores Competitivo",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/Multiplayer"})
    create_element("Open Ended","Final em Aberto",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/No_Game_End"})
    create_element("Dificulty Level","Nível de Dificuldade",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/Difficulty_Levels"})
    create_element("Character Customization","Personalização de Personagem",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/Character_customization"})
    create_element("Challenge Segmentation","Desafios Segmentados",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/Challenge_Segmentation"})
    create_element("Spatial Segmentation","Segmentação Espacial",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/Spatial_Segmentation"})
    create_element("Temporal Segmentation","Segmentação Temporal",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/Temporal_Segmentation"})
    create_element("Narrative Segmentation","Segmentação Narrativa",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/Narrative_Segmentation"})
    create_element("Boss Challenge","Desafio de Chefes",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/Boss_Challenge"})
    create_element("Bonus Stage","Fase Bônus",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/Bonus_Stage"})
    create_element("Puzzle","Enigmas",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/Puzzle"})
    create_element("Mission","Missão",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/Mission"})
    create_element("Temporal Coordination","Coordenação Temporizada",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/Temporal_Coordination"})
    create_element("Temporal Resource","Recurso por Tempo",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/Temporal_Resource"})
    create_element("Turn Based Game","Jogo por Turnos",
        {"type":"single", "source":"text", "ref":"Turn Based Games like Chess, Go or the majority of board games."})
    create_element("Cropping","Cropping",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/Cropping"})
    create_element("Expiration","Expiração",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/Expiration"})
    create_element("Physical Rules","Regras Físicas",
        {"type":"single", "source":"text", "ref":"No Reference. Check out Pseudo-Physical Rules"})
    create_element("Pseudo-Physical Rules","Regras Pseudo Físicas",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/Pseudo-Physical_Rules"})
    create_element("Savepoint","Ponto de Gravação",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/Savepoint"})
    create_element("Compound Actions","Ações Compostas",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/Compound_Action"})
    create_element("To Manage","Gerenciar",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/To_Manage_Resources"})
    create_element("To Transport","Transportar",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/To_Transport"})
    create_element("To Colide","Colidir",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/To_Collide"})
    create_element("To Create","Criar",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/To_Create"})
    create_element("To Generate","Gerar",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/To_Generate"})
    create_element("To Move","Mover",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/To_Move"})
    create_element("To Teleport","Teleportar",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/To_Teleport"})
    create_element("To Own","Apropriar",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/To_Own"})
    create_element("To Exchange","Trocar",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/To_Exchange"})
    create_element("To Possess","Possuir",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/To_Possess"})
    create_element("To Collect","Coletar",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/To_Collect"})
    create_element("To Release","Liberar",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/To_Release"})
    create_element("To Transfer","Transferir",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/To_Transfer"})
    create_element("To Remove","Remover",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/To_Remove"})
    create_element("To Rotate","Rotacionar",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/To_Rotate"})
    create_element("To Select","Selecionar",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/To_Select"})
    create_element("To Target","Definir",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/To_Target"})
    create_element("To Manipulate Time","Manipular Tempo",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/To_Manipulate_Time"})
    create_element("To Start Time","Iniciar Tempo",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/To_Start_Time"})
    create_element("To Pause Time","Pausar Tempo",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/To_Pause_Time"})
    create_element("To Rewind Time","Retroceder no Tempo",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/To_Rewind_Time"})
    create_element("To Fast Forward","Avançar no Tempo",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/To_Fast_Forward_Time"})
    create_element("To Accelerate Time","Acelerar Tempo",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/To_Accelerate_Time"})
    create_element("To Decelerate Time","Retardar Tempo",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/To_Decelerate_Time"})
    create_element("To Localize Time","Localizar no Tempo",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/To_Localize_Time"})
    create_element("To Manipulate Gravity","Manipular Gravidade",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/Gravity_Manipulation"})
    create_element("To Customize","Personalizar",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/To_Customize"})
    create_element("In-game Customization","Personalização em Jogo",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/In-game_Customization"})
    create_element("Customization via Game Menu","Personalização via Menu de Jogo",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/Customization_via_Game_Menu"})
    create_element("External Game Customization","Customização de Jogo Externa",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/Extra-game_Customization"})
    create_element("Goals","Objetivos",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/Goals"})
    create_element("Agent Goals","Objetivos de Agentes",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/Agent_Goals"})
    create_element("Game Goals","Objetivos de Jogo",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/Game_Goals"})
    create_element("Required Goals","Objetivos Especificados",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/Required_Goals"})
    create_element("Collectibles","Colecionáveis",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/Collectables"})
    create_element("Side Quests","Tarefas não Principais",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/Side-Quest"})
    create_element("Performance Record","Registro de Performance",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/Performance_Record"})
    create_element("Score","Pontuação",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/Score"})
    create_element("Hi-Score","Hi-Score",
        {"type":"single", "source":"Text", "ref":"No Reference."})
    create_element("Success Level","Nível de Sucesso",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/Success_Level"})
    create_element("Time Success Measurement","Mensuração de Sucesso por Tempo",
        {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/Time"})
    create_element("To Undo Time","Desfazer (Tempo)", {"type":"single", "source":"link", "ref":"http://www.gameontology.com/index.php/To_Undo_Time"})
