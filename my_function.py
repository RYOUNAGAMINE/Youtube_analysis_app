def get_key(val,id_title):
    for key, value in id_title.items():
        if val == value:
            return key

def country_name(code):
    country_code_dictionary = {
        'JP' : '日本',
        'TW' : '台湾',
        'HK' : '香港',
        'US' : 'アメリカ',
        'TH' : 'タイ',
        'MX' : 'メキシコ',
        'ID' : 'インドネシア'
    }
    for key, value in country_code_dictionary.items():
        if code == key:
            return value
    return('不明な国')

def device_name(device_code):
    device_code_dictionary = {
        'DESKTOP' : 'パソコン',
        'GAME_CONSOLE' : 'ゲームコンソール',
        'MOBILE' : '携帯',
        'TABLET' : 'タブレット',
        'TV' : 'テレビ',
        'UNKNOWN_PLATFORM' : '不明なデバイス'
    }
    for key, value in device_code_dictionary.items():
        if device_code == key:
            return value