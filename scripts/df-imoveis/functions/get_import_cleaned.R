#' @title Pré-processamento 
#' @title Luiz Paulo Tavares 

get_data_cleaned <- function(db){
  
  data_raw = db %>% 
             janitor::clean_names() %>% 
             dplyr::mutate(property_type = case_when(
                            grepl("APARTAMENTO", type, ignore.case = TRUE) ~ "Apartamento",
                            grepl("CASA CONDOMINIO", type, ignore.case = TRUE) ~ "Casa Condominio",
                            grepl("CASA", type, ignore.case = TRUE) ~ "Casa", TRUE ~ "Outro")) %>%  
            dplyr::mutate(location = case_when(
                            grepl("BRASILIA", description, ignore.case = TRUE) ~ "Brasilia",
                            grepl("AGUAS CLARAS", description, ignore.case = TRUE) ~ "Aguas Claras",
                            grepl("JARDIM BOTANICO", description, ignore.case = TRUE) ~ "Jardim Botanico",
                            grepl("SOBRADINHO", description, ignore.case = TRUE) ~ "Sobradinho",
                            grepl("VICENTE PIRES", description, ignore.case = TRUE) ~ "Vicente Pires",
                            grepl("TAGUATINGA", description, ignore.case = TRUE) ~ "Taguatinga",
                            grepl("GUARA", description, ignore.case = TRUE) ~ "Guara",
                            grepl("SAMAMBAIA", description, ignore.case = TRUE) ~ "Samambaia",
                            grepl("CEILANDIA", description, ignore.case = TRUE) ~ "Ceilandia",
                            grepl("GAMA", description, ignore.case = TRUE) ~ "Gama",
                            grepl("RIACHO FUNDO", description, ignore.case = TRUE) ~ "Riacho Fundo",
                            grepl("VALPARAISO DE GOIAS", description, ignore.case = TRUE) ~ "Valparaiso de Goias",
                            grepl("NUCLEO BANDEIRANTE", description, ignore.case = TRUE) ~ "Nucleo Bandeirante",
                            grepl("SAO SEBASTIAO", description, ignore.case = TRUE) ~ "Sao Sebastiao",
                            grepl("RECANTO DAS EMAS", description, ignore.case = TRUE) ~ "Recanto das Emas",
                            grepl("CRUZEIRO", description, ignore.case = TRUE) ~ "Cruzeiro",
                            grepl("PARANOA", description, ignore.case = TRUE) ~ "Paranoa",
                            grepl("PLANALTINA", description, ignore.case = TRUE) ~ "Planaltina",
                            grepl("CIDADE OCIDENTAL", description, ignore.case = TRUE) ~ "Cidade Ocidental",
                            grepl("SANTA MARIA", description, ignore.case = TRUE) ~ "Santa Maria",
                            grepl("ALPHAVILLE", description, ignore.case = TRUE) ~ "Alphaville",
                            grepl("LUZIANIA", description, ignore.case = TRUE) ~ "Luziania",
                            grepl("SETOR INDUSTRIAL", description, ignore.case = TRUE) ~ "Setor Industrial",
                            grepl("AGUAS LINDAS DE GOIAS", description, ignore.case = TRUE) ~ "Aguas Lindas de Goias",
                            grepl("CANDANGOLANDIA", description, ignore.case = TRUE) ~ "Candangolandia",
                            grepl("BRAZLANDIA", description, ignore.case = TRUE) ~ "Brazlandia",
                            grepl("SANTO ANTONIO DO DESCOBERTO", description, ignore.case = TRUE) ~ "Santo Antonio do Descoberto",
                            grepl("FORMOSA", description, ignore.case = TRUE) ~ "Formosa",
                            grepl("PLANALTINA DE GOIAS", description, ignore.case = TRUE) ~ "Planaltina de Goias",
                            grepl("VILA ESTRUTURAL", description, ignore.case = TRUE) ~ "Vila Estrutural",
                            grepl("VARJAO", description, ignore.case = TRUE) ~ "Varjao",
                            TRUE ~ "Outro"))  %>% 
           dplyr::filter(property_type != "Outro") 
  
  
  data_cleaned <- data_raw %>% 
                  dplyr::mutate(price = as.numeric(base::gsub("\\.", "", price)), 
                                size = as.numeric(base::gsub("m²", "", size)),
                                bedrooms = as.integer(str_sub(bedrooms, start = 1, end = 1)), 
                                car_spaces = as.integer(str_sub(car_spaces, start = 1, end = 1))) %>% 
                  dplyr::filter(!is.na(price) & 
                                  price > 0 & 
                                  size > 0) %>% 
                  dplyr::mutate(price_m2 = (price/size)) %>% 
                  dplyr::relocate(property_type, .after = description) %>% 
                  dplyr::relocate(location, .after = NULL) %>% 
                  dplyr::select(-description, -type) 
  
  return(data_cleaned)
  
}

