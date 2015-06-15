import os.path

def test_loadLang():
    import lang_le as lang
    # Test lang parent adresare 
    assert os.path.split(lang._d)[1]=="LayerEditor"
    # Test inicializace tridy pro lokalizaci
    assert type(lang._t).__name__=="GNUTranslations"
    # Test souboru s lokalizaci
    assert len(lang._t._catalog)>0
    
    
