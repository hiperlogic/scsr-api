from scsr.models.elements import ElementAO,ElementReferenceAO


def create_element(enName,ptName, refs):
    el=ElementAO()
    el.add_name('en',enName)
    el.add_name('pt',ptName)
    el.save()# TODO: Create the ElementReference representation and code the reference adding here.
    er=ElementReferenceAO.get_reference(el)
    er.set_reference(refs)
    er.save()


def start_derived():
    create_element("To Aim","Mirar", {"type":"single", "source":"link", "ref":"http://virt10.itu.chalmers.se/index.php/Aim_%26_Shoot"})
