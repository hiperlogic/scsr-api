from scsr.models.elements import ElementAO, ElementReferenceAO


def create_element(enName,ptName, refs):
    el=ElementAO()
    el.add_name('en',enName)
    el.add_name('pt',ptName)
    el.save()# TODO: Create the ElementReference representation and code the reference adding here.
    er=ElementReferenceAO.get_reference(el)
    er.set_reference(refs)
    er.save()



def start_multiple():
    create_element("Dynamic Difficulty Adjustment","Ajuste Dinâmico de Dificuldade",
        {"type":"multi", "source":"link", "ref":["http://www.gameontology.com/index.php/Dynamic_Difficulty_Adjustment","http://virt10.itu.chalmers.se/index.php/Dynamic_Difficulty_Adjustment"]})
    create_element("Lives","Vidas",
        {"type":"multi", "source":"link", "ref":["http://www.gameontology.com/index.php/Lives","http://virt10.itu.chalmers.se/index.php/Lives"]})
    create_element("Multiplayer","Multijogadores",
        {"type":"multi", "source":"link", "ref":["http://www.gameontology.com/index.php/Multiplayer","http://virt10.itu.chalmers.se/index.php/Multiplayer_Games"]})
    create_element("Randomness","Aleatoriedade",
        {"type":"multi", "source":"link", "ref":["http://www.gameontology.com/index.php/Randomness","http://virt10.itu.chalmers.se/index.php/Randomness"]})
    create_element("Wave","Onda",
        {"type":"multi", "source":"link", "ref":["http://www.gameontology.com/index.php/Wave", "http://virt10.itu.chalmers.se/index.php/Waves"]})
    create_element("Level","Nivel",
        {"type":"multi", "source":"link", "ref":["http://www.gameontology.com/index.php/Level","http://virt10.itu.chalmers.se/index.php/Levels"]})
    create_element("Spawn Point","Ponto de Início",
        {"type":"multi", "source":"link", "ref":["http://www.gameontology.com/index.php/Spawnpoint","http://virt10.itu.chalmers.se/index.php/Spawn_Points"]})
    create_element("To Shoot","Atirar",
        {"type":"multi", "source":"link", "ref":["http://www.gameontology.com/index.php/To_Shoot","http://virt10.itu.chalmers.se/index.php/Aim_%26_Shoot"]})
    create_element("To Evade","Desviar",
        {"type":"multi", "source":"link", "ref":["http://www.gameontology.com/index.php/To_Evade","http://virt10.itu.chalmers.se/index.php/Evade"]})
    create_element("To Traverse","Cruzar",
        {"type":"multi", "source":"link", "ref":["http://www.gameontology.com/index.php/To_Traverse","http://virt10.itu.chalmers.se/index.php/Traverse"]})
    create_element("To Visit","Visitar",
        {"type":"multi", "source":"link", "ref":["http://www.gameontology.com/index.php/To_Visit","http://virt10.itu.chalmers.se/index.php/Visits"], "ambiguity":True})
    create_element("To Capture","Capturar",
        {"type":"multi", "source":"link", "ref":["http://www.gameontology.com/index.php/To_Capture","http://virt10.itu.chalmers.se/index.php/Capture"]})
    create_element("Optional Goals","Objetivos Opcionais",
        {"type":"multi", "source":"link", "ref":["http://www.gameontology.com/index.php/Optional_Goals","http://virt10.itu.chalmers.se/index.php/Optional_Goals"]})
    create_element("Checkpoint","Checkpoint",
        {"type":"multi", "source":"link", "ref":["http://www.gameontology.com/index.php/Spatial_Checkpoint","http://virt10.itu.chalmers.se/index.php/Check_Points"]})
    create_element("Head Up Display (HUD)","Interface HUD",
        {"type":"multi","source":"link", "ref":["http://www.gameontology.com/index.php/Head_Up_Display","http://virt10.itu.chalmers.se/index.php/HUD_Interfaces"]})

