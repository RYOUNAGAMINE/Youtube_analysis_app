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

