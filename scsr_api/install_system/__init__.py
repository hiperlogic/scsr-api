"""
    This is the installation routines for the system.
    It does:
    1 - Drop all previous database (this is not a Maintenance system! Beware!)
    2 - Sets up the language collection containing all ISO 639-1 language codes and their respective english names
    3 - Sets up the genre collection with the usual game genres as provived by Crawford. In 'en' and 'pt'.
    4 - Sets up the elements listed in the Game Ontology and in the Patterns in Game Design. In 'en' and 'pt'.
        - This provides a quick guide for users to start classifying the games.
    5 - Sets up the first administrative account.
    6 - Sets up three games: Tetris, Pac Man and Space Invaders, with no subjective setting assigned (Genre or SCSR classification)
"""

from uuid import uuid4
from datetime import datetime

from application import db
from game.models.game import GameAO
from game.models.genre import GenreAO
from utils.models.lang_code import lang_codeDB
from utils.models.country_code import country_codeDB
from scsr.models.elements import ElementAO
from admin.models.admin import AdminDB, AdminGroupDB
from user.models.user import UserAO

#The ISO 639-1 language codes
lang_codes={
    "ab":{"en":["Abkhazian"]},
    "aa":{"en":["Afar"]},
    "af":{"en":["Afrikaans"]},
    "ak":{"en":["Akan"]},
    "sq":{"en":["Albanian"]},
    "am":{"en":["Amharic"]},
    "ar":{"en":["Arabic"]},
    "an":{"en":["Aragonese"]},
    "hy":{"en":["Armenian"]},
    "as":{"en":["Assamese"]},
    "av":{"en":["Avaric"]},
    "ae":{"en":["Avestan"]},
    "ay":{"en":["Aymara"]},
    "az":{"en":["Azerbaijani"]},
    "bm":{"en":["Bambara"]},
    "ba":{"en":["Bashkir"]},
    "eu":{"en":["Basque"]},
    "be":{"en":["Belarusian"]},
    "bn":{"en":["Bengali (Bangla)"]},
    "bh":{"en":["Bihari"]},
    "bi":{"en":["Bislama"]},
    "bs":{"en":["Bosnian"]},
    "br":{"en":["Breton"]},
    "bg":{"en":["Bulgarian"]},
    "my":{"en":["Burmese"]},
    "ca":{"en":["Catalan"]},
    "ch":{"en":["Chamorro"]},
    "ce":{"en":["Chechen"]},
    "ny":{"en":["Chichewa","Chewa", "Nyanja"]},
    "zh":{"en":["Chinese"]},
    "zh-Hans":{"en":["Chinese (Simplified)"]},
    "zh-Hant":{"en":["Chinese (Traditional)"]},
    "cv":{"en":["Chuvash"]},
    "kw":{"en":["Cornish"]},
    "co":{"en":["Corsican"]},
    "cr":{"en":["Cree"]},
    "hr":{"en":["Croatian"]},
    "cs":{"en":["Czech"]},
    "da":{"en":["Danish"]},
    "dv":{"en":["Divehi", "Dhivehi", "Maldivian"]},
    "nl":{"en":["Dutch"]},
    "dz":{"en":["Dzongkha"]},
    "en":{"en":["English"]},
    "eo":{"en":["Esperanto"]},
    "et":{"en":["Estonian"]},
    "ee":{"en":["Ewe"]},
    "fo":{"en":["Faroese"]},
    "fj":{"en":["Fijian"]},
    "fi":{"en":["Finnish"]},
    "fr":{"en":["French"]},
    "ff":{"en":["Fula", "Fulah", "Pulaar", "Pular"]},
    "gl":{"en":["Galician"]},
    "gd":{"en":["Gaelic (Scottish)"]},
    "gv":{"en":["Gaelic (Manx)","Manx"]},
    "ka":{"en":["Georgian"]},
    "de":{"en":["German"]},
    "el":{"en":["Greek"]},
    "gn":{"en":["Guarani"]},
    "gu":{"en":["Gujarati"]},
    "ht":{"en":["Haitian Creole"]},
    "ha":{"en":["Hausa"]},
    "he":{"en":["Hebrew"]},
    "hz":{"en":["Herero"]},
    "hi":{"en":["Hindi"]},
    "ho":{"en":["Hiri Motu"]},
    "hu":{"en":["Hungarian"]},
    "is":{"en":["Icelandic"]},
    "io":{"en":["Ido"]},
    "ig":{"en":["Igbo"]},
    "in":{"en":["Indonesian"]},
    "id":{"en":["Indonesian"]},
    "ia":{"en":["Interlingua"]},
    "ie":{"en":["Interlingue"]},
    "iu":{"en":["Inuktitut"]},
    "ik":{"en":["Inupiak"]},
    "ga":{"en":["Irish"]},
    "it":{"en":["Italian"]},
    "ja":{"en":["Japanese"]},
    "jv":{"en":["Javanese"]},
    "kl":{"en":["Kalaallisut", "Greenlandic"]},
    "kn":{"en":["Kannada"]},
    "kr":{"en":["Kanuri"]},
    "ks":{"en":["Kashmiri"]},
    "kk":{"en":["Kazakh"]},
    "km":{"en":["Khmer"]},
    "ki":{"en":["Kikuyu"]},
    "rw":{"en":["Kinyarwanda (Rwanda)"]},
    "rn":{"en":["Kirundi"]},
    "ky":{"en":["Kyrgyz"]},
    "kv":{"en":["Komi"]},
    "kg":{"en":["Kongo"]},
    "ko":{"en":["Korean"]},
    "ku":{"en":["Kurdish"]},
    "kj":{"en":["Kwanyama"]},
    "lo":{"en":["Lao"]},
    "la":{"en":["Latin"]},
    "lv":{"en":["Latvian (Lettish)"]},
    "li":{"en":["Limburgish (Limburger)"]},
    "ln":{"en":["Lingala"]},
    "lt":{"en":["Lithuanian"]},
    "lu":{"en":["Luga","Katanga"]},
    "lg":{"en":["Luganda", "Ganda"]},
    "lb":{"en":["Luxembourgish"]},
    "mk":{"en":["Macedonian"]},
    "mg":{"en":["Malagasy"]},
    "ms":{"en":["Malay"]},
    "ml":{"en":["Malayalam"]},
    "mt":{"en":["Maltese"]},
    "mi":{"en":["Maori"]},
    "mr":{"en":["Marathi"]},
    "mh":{"en":["Marshallese"]},
    "mo":{"en":["Moldavian"]},
    "mn":{"en":["Mongolian"]},
    "na":{"en":["Nauru"]},
    "nv":{"en":["Navajo"]},
    "ng":{"en":["Ndonga"]},
    "nd":{"en":["Northern Ndebele"]},
    "ne":{"en":["Nepali"]},
    "no":{"en":["Norwegian"]},
    "nb":{"en":["Norwegian bokmål"]},
    "nn":{"en":["Norwegian nynorsk"]},
    "ii":{"en":["Nuosu", "Sichuan Yi"]},
    "oc":{"en":["Occitan"]},
    "oj":{"en":["Ojibwe"]},
    "cu":{"en":["Old Church Slavonic", "Old Bulgarian"]},
    "or":{"en":["Oriya"]},
    "om":{"en":["Oromo (Afaan Oromo)"]},
    "os":{"en":["Ossetian"]},
    "pi":{"en":["Pāli"]},
    "ps":{"en":["Pashto", "Pushto"]},
    "fa":{"en":["Persian (Farsi)"]},
    "pl":{"en":["Polish"]},
    "pt":{"en":["Portuguese"]},
    "pa":{"en":["Punjabi (Eastern)"]},
    "qu":{"en":["Quechua"]},
    "rm":{"en":["Romansh"]},
    "ro":{"en":["Romanian"]},
    "ru":{"en":["Russian"]},
    "se":{"en":["Sami"]},
    "sm":{"en":["Samoan"]},
    "sg":{"en":["Sango"]},
    "sa":{"en":["Sanskrit"]},
    "sr":{"en":["Serbian"]},
    "sh":{"en":["Serbo-Croatian"]},
    "st":{"en":["Sesotho"]},
    "tn":{"en":["Setswana"]},
    "sn":{"en":["Shona"]},
    "sd":{"en":["Sindhi"]},
    "si":{"en":["Sinhalese"]},
    "ss":{"en":["Siswati", "Swati"]},
    "sk":{"en":["Slovak"]},
    "sl":{"en":["Slovenian"]},
    "so":{"en":["Somali"]},
    "nr":{"en":["Southern Ndebele"]},
    "es":{"en":["Spanish"]},
    "su":{"en":["Sundanese"]},
    "sw":{"en":["Swahili (Kiswahili)"]},
    "sv":{"en":["Swedish"]},
    "tl":{"en":["Tagalog"]},
    "ty":{"en":["Tahitian"]},
    "tg":{"en":["Tajik"]},
    "ta":{"en":["Tamil"]},
    "tt":{"en":["Tatar"]},
    "te":{"en":["Telugu"]},
    "th":{"en":["Thai"]},
    "bo":{"en":["Tibetan"]},
    "ti":{"en":["Tigrinya"]},
    "to":{"en":["Tonga"]},
    "ts":{"en":["Tsonga"]},
    "tr":{"en":["Turkish"]},
    "tk":{"en":["Turkmen"]},
    "tw":{"en":["Twi"]},
    "ug":{"en":["Uyghur"]},
    "uk":{"en":["Ukrainian"]},
    "ur":{"en":["Urdu"]},
    "uz":{"en":["Uzbek"]},
    "ve":{"en":["Venda"]},
    "vi":{"en":["Vietnamese"]},
    "vo":{"en":["Volapük"]},
    "wa":{"en":["Wallon"]},
    "cy":{"en":["Welsh"]},
    "wo":{"en":["Wolof"]},
    "fy":{"en":["Western Frisian"]},
    "xh":{"en":["Xhosa"]},
    "ji":{"en":["Yiddish"]},
    "yi":{"en":["Yiddish"]},
    "yo":{"en":["Yoruba"]},
    "za":{"en":["Zhuang","Chuang"]},
    "zu":{"en":["Zulu"]}
}

countries_codes={
    "AF":{"en":"Afghanistan"},	
    "AX":{"en":"Åland Islands"},	
    "AL":{"en":"Albania"},	
    "DZ":{"en":"Algeria"},	
    "AS":{"en":"American Samoa"},	
    "AD":{"en":"Andorra"},	
    "AO":{"en":"Angola"},	
    "AI":{"en":"Anguilla"},	
    "AQ":{"en":"Antarctica"},	
    "AG":{"en":"Antigua and Barbuda"},	
    "AR":{"en":"Argentina"},	
    "AM":{"en":"Armenia"},	
    "AW":{"en":"Aruba"},	
    "AU":{"en":"Australia"},	
    "AT":{"en":"Austria"},	
    "AZ":{"en":"Azerbaijan"},	
    "BH":{"en":"Bahrain"},	
    "BS":{"en":"Bahamas"},	
    "BD":{"en":"Bangladesh"},	
    "BB":{"en":"Barbados"},	
    "BY":{"en":"Belarus"},	
    "BE":{"en":"Belgium"},	
    "BZ":{"en":"Belize"},	
    "BJ":{"en":"Benin"},	
    "BM":{"en":"Bermuda"},	
    "BT":{"en":"Bhutan"},	
    "BO":{"en":"Bolivia, Plurinational State of"},	
    "BQ":{"en":"Bonaire, Sint Eustatius and Saba"},	
    "BA":{"en":"Bosnia and Herzegovina"},	
    "BW":{"en":"Botswana"},	
    "BV":{"en":"Bouvet Island"},	
    "BR":{"en":"Brazil"},	
    "IO":{"en":"British Indian Ocean Territory"},	
    "BN":{"en":"Brunei Darussalam"},	
    "BG":{"en":"Bulgaria"},	
    "BF":{"en":"Burkina Faso"},	
    "BI":{"en":"Burundi"},	
    "KH":{"en":"Cambodia"},	
    "CM":{"en":"Cameroon"},	
    "CA":{"en":"Canada"},	
    "CV":{"en":"Cape Verde"},	
    "KY":{"en":"Cayman Islands"},	
    "CF":{"en":"Central African Republic"},	
    "TD":{"en":"Chad"},	
    "CL":{"en":"Chile"},	
    "CN":{"en":"China"},	
    "CX":{"en":"Christmas Island"},	
    "CC":{"en":"Cocos (Keeling) Islands"},	
    "CO":{"en":"Colombia"},	
    "KM":{"en":"Comoros"},	
    "CG":{"en":"Congo"},	
    "CD":{"en":"Congo, the Democratic Republic of the"},	
    "CK":{"en":"Cook Islands"},	
    "CR":{"en":"Costa Rica"},	
    "CI":{"en":"Côte d'Ivoire"},	
    "HR":{"en":"Croatia"},	
    "CU":{"en":"Cuba"},	
    "CW":{"en":"Curaçao"},	
    "CY":{"en":"Cyprus"},	
    "CZ":{"en":"Czech Republic"},	
    "DK":{"en":"Denmark"},	
    "DJ":{"en":"Djibouti"},	
    "DM":{"en":"Dominica"},	
    "DO":{"en":"Dominican Republic"},	
    "EC":{"en":"Ecuador"},	
    "EG":{"en":"Egypt"},	
    "SV":{"en":"El Salvador"},	
    "GQ":{"en":"Equatorial Guinea"},	
    "ER":{"en":"Eritrea"},	
    "EE":{"en":"Estonia"},	
    "ET":{"en":"Ethiopia"},	
    "FK":{"en":"Falkland Islands (Malvinas)"},	
    "FO":{"en":"Faroe Islands"},	
    "FJ":{"en":"Fiji"},	
    "FI":{"en":"Finland"},	
    "FR":{"en":"France"},	
    "GF":{"en":"French Guiana"},	
    "PF":{"en":"French Polynesia"},	
    "TF":{"en":"French Southern Territories"},	
    "GA":{"en":"Gabon"},	
    "GM":{"en":"Gambia"},	
    "GE":{"en":"Georgia"},	
    "DE":{"en":"Germany"},	
    "GH":{"en":"Ghana"},	
    "GI":{"en":"Gibraltar"},	
    "GR":{"en":"Greece"},	
    "GL":{"en":"Greenland"},	
    "GD":{"en":"Grenada"},	
    "GP":{"en":"Guadeloupe"},	
    "GU":{"en":"Guam"},	
    "GT":{"en":"Guatemala"},	
    "GG":{"en":"Guernsey"},	
    "GN":{"en":"Guinea"},	
    "GW":{"en":"Guinea-Bissau"},	
    "GY":{"en":"Guyana"},	
    "HT":{"en":"Haiti"},	
    "HM":{"en":"Heard Island and McDonald Islands"},	
    "VA":{"en":"Holy See (Vatican City State)"},	
    "HN":{"en":"Honduras"},	
    "HK":{"en":"Hong Kong"},	
    "HU":{"en":"Hungary"},	
    "IS":{"en":"Iceland"},	
    "IN":{"en":"India"},	
    "ID":{"en":"Indonesia"},	
    "IR":{"en":"Iran, Islamic Republic of"},	
    "IQ":{"en":"Iraq"},	
    "IE":{"en":"Ireland"},	
    "IM":{"en":"Isle of Man"},	
    "IL":{"en":"Israel"},	
    "IT":{"en":"Italy"},	
    "JM":{"en":"Jamaica"},	
    "JP":{"en":"Japan"},	
    "JE":{"en":"Jersey"},	
    "JO":{"en":"Jordan"},	
    "KZ":{"en":"Kazakhstan"},	
    "KE":{"en":"Kenya"},	
    "KI":{"en":"Kiribati"},	
    "KP":{"en":"Korea, Democratic People's Republic of"},	
    "KR":{"en":"Korea, Republic of"},	
    "KW":{"en":"Kuwait"},	
    "KG":{"en":"Kyrgyzstan"},	
    "LA":{"en":"Lao People's Democratic Republic"},	
    "LV":{"en":"Latvia"},	
    "LB":{"en":"Lebanon"},	
    "LS":{"en":"Lesotho"},	
    "LR":{"en":"Liberia"},	
    "LY":{"en":"Libya"},	
    "LI":{"en":"Liechtenstein"},	
    "LT":{"en":"Lithuania"},	
    "LU":{"en":"Luxembourg"},	
    "MO":{"en":"Macao"},	
    "MK":{"en":"Macedonia, the Former Yugoslav Republic of"},	
    "MG":{"en":"Madagascar"},	
    "MW":{"en":"Malawi"},	
    "MY":{"en":"Malaysia"},	
    "MV":{"en":"Maldives"},	
    "ML":{"en":"Mali"},	
    "MT":{"en":"Malta"},	
    "MH":{"en":"Marshall Islands"},	
    "MQ":{"en":"Martinique"},	
    "MR":{"en":"Mauritania"},	
    "MU":{"en":"Mauritius"},	
    "YT":{"en":"Mayotte"},	
    "MX":{"en":"Mexico"},	
    "FM":{"en":"Micronesia, Federated States of"},	
    "MD":{"en":"Moldova, Republic of"},	
    "MC":{"en":"Monaco"},	
    "MN":{"en":"Mongolia"},	
    "ME":{"en":"Montenegro"},	
    "MS":{"en":"Montserrat"},	
    "MA":{"en":"Morocco"},	
    "MZ":{"en":"Mozambique"},	
    "MM":{"en":"Myanmar"},	
    "NA":{"en":"Namibia"},	
    "NR":{"en":"Nauru"},	
    "NP":{"en":"Nepal"},	
    "NL":{"en":"Netherlands"},	
    "NC":{"en":"New Caledonia"},	
    "NZ":{"en":"New Zealand"},	
    "NI":{"en":"Nicaragua"},	
    "NE":{"en":"Niger"},	
    "NG":{"en":"Nigeria"},	
    "NU":{"en":"Niue"},	
    "NF":{"en":"Norfolk Island"},	
    "MP":{"en":"Northern Mariana Islands"},	
    "NO":{"en":"Norway"},	
    "OM":{"en":"Oman"},	
    "PK":{"en":"Pakistan"},	
    "PW":{"en":"Palau"},	
    "PS":{"en":"Palestine, State of"},	
    "PA":{"en":"Panama"},	
    "PG":{"en":"Papua New Guinea"},	
    "PY":{"en":"Paraguay"},	
    "PE":{"en":"Peru"},	
    "PH":{"en":"Philippines"},	
    "PN":{"en":"Pitcairn"},	
    "PL":{"en":"Poland"},	
    "PT":{"en":"Portugal"},	
    "PR":{"en":"Puerto Rico"},	
    "QA":{"en":"Qatar"},	
    "RE":{"en":"Réunion"},	
    "RO":{"en":"Romania"},	
    "RU":{"en":"Russian Federation"},	
    "RW":{"en":"Rwanda"},	
    "BL":{"en":"Saint Barthélemy"},	
    "SH":{"en":"Saint Helena, Ascension and Tristan da Cunha"},	
    "KN":{"en":"Saint Kitts and Nevis"},	
    "LC":{"en":"Saint Lucia"},	
    "MF":{"en":"Saint Martin (French part)"},	
    "PM":{"en":"Saint Pierre and Miquelon"},	
    "VC":{"en":"Saint Vincent and the Grenadines"},	
    "WS":{"en":"Samoa"},	
    "SM":{"en":"San Marino"},	
    "ST":{"en":"Sao Tome and Principe"},	
    "SA":{"en":"Saudi Arabia"},	
    "SN":{"en":"Senegal"},	
    "RS":{"en":"Serbia"},	
    "SC":{"en":"Seychelles"},	
    "SL":{"en":"Sierra Leone"},	
    "SG":{"en":"Singapore"},	
    "SX":{"en":"Sint Maarten (Dutch part)"},	
    "SK":{"en":"Slovakia"},	
    "SI":{"en":"Slovenia"},	
    "SB":{"en":"Solomon Islands"},	
    "SO":{"en":"Somalia"},	
    "ZA":{"en":"South Africa"},	
    "GS":{"en":"South Georgia and the South Sandwich Islands"},	
    "SS":{"en":"South Sudan"},	
    "ES":{"en":"Spain"},	
    "LK":{"en":"Sri Lanka"},	
    "SD":{"en":"Sudan"},	
    "SR":{"en":"Suriname"},	
    "SJ":{"en":"Svalbard and Jan Mayen"},	
    "SZ":{"en":"Swaziland"},	
    "SE":{"en":"Sweden"},	
    "CH":{"en":"Switzerland"},	
    "SY":{"en":"Syrian Arab Republic"},	
    "TW":{"en":"Taiwan, Province of China"},	
    "TJ":{"en":"Tajikistan"},	
    "TZ":{"en":"Tanzania, United Republic of"},	
    "TH":{"en":"Thailand"},	
    "TL":{"en":"Timor-Leste"},	
    "TG":{"en":"Togo"},	
    "TK":{"en":"Tokelau"},	
    "TO":{"en":"Tonga"},	
    "TT":{"en":"Trinidad and Tobago"},	
    "TN":{"en":"Tunisia"},	
    "TR":{"en":"Turkey"},	
    "TM":{"en":"Turkmenistan"},	
    "TC":{"en":"Turks and Caicos Islands"},	
    "TV":{"en":"Tuvalu"},	
    "UG":{"en":"Uganda"},	
    "UA":{"en":"Ukraine"},	
    "AE":{"en":"United Arab Emirates"},	
    "GB":{"en":"United Kingdom"},	
    "US":{"en":"United States"},	
    "UM":{"en":"United States Minor Outlying Islands"},	
    "UY":{"en":"Uruguay"},	
    "UZ":{"en":"Uzbekistan"},	
    "VU":{"en":"Vanuatu"},	
    "VE":{"en":"Venezuela, Bolivarian Republic of"},	
    "VN":{"en":"Viet Nam"},	
    "VG":{"en":"Virgin Islands, British"},	
    "VI":{"en":"Virgin Islands, U.S."},	
    "WF":{"en":"Wallis and Futuna"},	
    "EH":{"en":"Western Sahara"},	
    "YE":{"en":"Yemen"},	
    "ZM":{"en":"Zambia"},	
    "ZW":{"en":"Zimbabwe"}
}
"""Starts the language data in the database
   Status: Ok
"""

def start_language():
    for key in lang_codes.keys():
        theCode=lang_codeDB()
        theCode.code=key
        theCode.lang=lang_codes[key]
        if(key in ['pt','en']):
            theCode.in_system=True
        theCode.save()

"""Starts the countries data in the database
   Status: Ok
"""
def start_countries():
    for key in countries_codes.keys():
        theCountry=country_codeDB()
        theCountry.code=key
        theCountry.country=countries_codes[key]
        theCountry.save()

"""Starts the admin groups data in the database
   Status: Ok for the first 2
"""
def start_admin_groups():
    GOD=AdminGroupDB()
    GOD.external_id=str(uuid4())
    GOD.group={'en':'GOD','pt':'DEUS'}
    GOD.save()
    common=AdminGroupDB()
    common.external_id=str(uuid4())
    common.group={"en":"common", "pt":"comum"}
    common.save()

def start_user(options={}):
    firstAdmin=UserAO()
    firstAdmin.set_username(options.get("username","admin"))
    firstAdmin.set_password(options.get("password","admin"))
    firstAdmin.set_country(options.get("country",country_codeDB.objects.filter(code="BR").first().code)) # pylint: disable=no-member
    firstAdmin.set_lang(options.get("lang",lang_codeDB.objects.filter(code="en").first().code)) # pylint: disable=no-member
    firstAdmin.set_name(options.get("name","firstName"))
    firstAdmin.set_surname(options.get("surname","surName"))
    firstAdmin.set_email(options.get("email","email@tofill.it"))
    firstAdmin.set_birthdate(options.get("birthdate",datetime(1977,8,10)))
    firstAdmin.save()
    theAdmin=AdminDB()
    """Important to notice. The group of the admin is a list, therefore there is no need to return the sole object of the list provided by the query.
    """
    theAdmin.group=AdminGroupDB.objects.filter(group__en="GOD") # pylint: disable=no-member
    theAdmin.set_admin(firstAdmin)
    theAdmin.save()

def start_genre():
    acao=GenreAO()
    acao.set_genre("pt","ação")
    acao.set_genre("en","action")
    acao.save()
    aventura=GenreAO()
    aventura.set_genre("pt","aventura")
    aventura.set_genre("en","adventure")
    aventura.save()
    simulacao=GenreAO()
    simulacao.set_genre("pt","simulação")
    simulacao.set_genre("en","simulation")
    simulacao.save()
    estrategia=GenreAO()
    estrategia.set_genre("pt","estratégia")
    estrategia.set_genre("en","strategy")
    estrategia.save()
    rpg=GenreAO()
    rpg.set_genre("pt","rpg")
    rpg.set_genre("en","rpg")
    rpg.save()
    puzzle=GenreAO()
    puzzle.set_genre("pt","enigma")
    puzzle.set_genre("en","puzzle")
    puzzle.save()
    casual=GenreAO()
    casual.set_genre("pt","casual")
    casual.set_genre("en","casual")
    casual.save()

def start_games():
    si=GameAO()
    si.set_name("pt","Space Invaders")
    si.set_name("en","Space Invaders")
    si.studio="Taito"
    si.publisher="Taito"
    si.year=datetime(year=1978, month=6, day=1)
    si.save()
    pm=GameAO()
    pm.set_name("pt","Pac Man")
    pm.set_name("en","Pac Man")
    pm.studio="Namco"
    pm.publisher="Namco"
    pm.year=datetime(year=1980, month=5, day=1)
    pm.save()
    tt=GameAO()
    tt.set_name("pt","Tetris")
    tt.set_name("en","Tetris")
    tt.studio="*"
    tt.publisher="*"
    tt.year=datetime(year=1984, month=6, day=1)
    tt.save()

def start_elements_ontology():
    from install_system.game_ontology import start_ontology
    start_ontology()
    
def start_elements_pigd():
    from install_system.patterns_game_design import start_pigd
    start_pigd()

def start_elements_multi():
    from install_system.multiple_sources import start_multiple
    start_multiple()

def start_elements_derived():
    from install_system.derived import start_derived
    start_derived()

def start_elements_machinations():
    from install_system.machinations import start_machinations
    start_machinations()

#effectively performs the data configuration
def start_system(options={}):
    start_language()
    start_countries()
    start_admin_groups()
    options=dict()

    print("Inform the admin data: ")
    options["username"]=input("Username:")
    options["password"]=input("password:")
    options["country"]=str(input("country code (2 letters):")).upper()
    options["lang"]=str(input("Language Code (2 letters):")).lower()
    options["name"]=input("First Name:")
    options["surname"]=input("Surname:")
    options["email"]=input("email:")
    try:
        options["birthdate"]=datetime.strptime(input("Birthdate (dd/mm/yyyy):"),"%d/%m/%Y")
    except:
        print("Error converting String to Date. (did you remembered to type the slashes?.. a generic date will be used.")

    start_user(options)
    start_genre()
    start_games()
    start_elements_ontology()
    start_elements_pigd()
    start_elements_multi()
    start_elements_derived()
    start_elements_machinations()
    #There we go! The system is ready for SCSR's
