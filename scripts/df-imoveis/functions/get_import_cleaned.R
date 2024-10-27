#' @title Pré-processamento 
#' @title Luiz Paulo Tavares 

get_data_cleaned <- function(db){
  
  data_raw = db %>% 
             janitor::clean_names() %>% 
             dplyr::mutate(property_type = case_when(
                            grepl("APARTAMENTO", type, ignore.case = TRUE) ~ "Apartamento",
                            # grepl("CASA CONDOMINIO", type, ignore.case = TRUE) ~ "Casa Condominio",
                            grepl("CASA", type, ignore.case = TRUE) ~ "Casa", TRUE ~ "Outros")) %>%  
            dplyr::mutate(location = case_when(
                            grepl("BRASILIA", description, ignore.case = TRUE) ~ "Brasilia",
                            grepl("GAMA", description, ignore.case = TRUE) ~ "Gama",
                            grepl("TAGUATINGA", description, ignore.case = TRUE) ~ "Taguatinga",
                            grepl("BRAZLANDIA", description, ignore.case = TRUE) ~ "Brazlandia",
                            grepl("SOBRADINHO", description, ignore.case = TRUE) ~ "Sobradinho",
                            grepl("PLANALTINA", description, ignore.case = TRUE) ~ "Planaltina",
                            grepl("PARANOA", description, ignore.case = TRUE) ~ "Paranoa",
                            grepl("NUCLEO BANDEIRANTE", description, ignore.case = TRUE) ~ "Nucleo Bandeirante",
                            grepl("CEILANDIA", description, ignore.case = TRUE) ~ "Ceilandia",
                            grepl("GUARA", description, ignore.case = TRUE) ~ "Guara",
                            grepl("CRUZEIRO", description, ignore.case = TRUE) ~ "Cruzeiro",
                            grepl("SAMAMBAIA", description, ignore.case = TRUE) ~ "Samambaia",
                            grepl("SANTA MARIA", description, ignore.case = TRUE) ~ "Santa Maria",
                            grepl("SAO SEBASTIAO", description, ignore.case = TRUE) ~ "Sao Sebastiao",
                            grepl("RECANTO DAS EMAS", description, ignore.case = TRUE) ~ "Recanto das Emas",
                            grepl("LAGO SUL", description, ignore.case = TRUE) ~ "Lago Sul", 
                            grepl("RIACHO FUNDO", description, ignore.case = TRUE) ~ "Riacho Fundo",
                            grepl("LAGO NORTE", description, ignore.case = TRUE) ~ "Lago Norte", 
                            grepl("CANDANGOLANDIA", description, ignore.case = TRUE) ~ "Candangolandia",
                            grepl("AGUAS CLARAS", description, ignore.case = TRUE) ~ "Aguas Claras",
                            grepl("RIACHO FUNDO II", description, ignore.case = TRUE) ~ "Riacho Fundo II",
                            grepl("SUDOESTE/OCTOGONAL", description, ignore.case = TRUE) ~ "Sudoeste Octogonal",
                            grepl("VARJAO", description, ignore.case = TRUE) ~ "Varjão",
                            grepl("PARK WAY", description, ignore.case = TRUE) ~ "Park Way",
                            grepl("SCIA", description, ignore.case = TRUE) ~ "SCIA",
                            grepl("SOBRADINHO II", description, ignore.case = TRUE) ~ "Sobradinho II",
                            grepl("JARDIM BOTANICO", description, ignore.case = TRUE) ~ "Jardim Botanico",
                            grepl("ITAPOA", description, ignore.case = TRUE) ~ "Itapoã",
                            grepl("SIA", description, ignore.case = TRUE) ~ "SIA",
                            grepl("VICENTE PIRES", description, ignore.case = TRUE) ~ "Vicente Pires",
                            grepl("FERCAL", description, ignore.case = TRUE) ~ "Fercal",
                            grepl("SOL NASCENTE/POR DO SOL", description, ignore.case = TRUE) ~ "Sol Nascente",
                            grepl("ARNIQUEIRA", description, ignore.case = TRUE) ~ "Arniqueira",
                            grepl("ARAPOANGA", description, ignore.case = TRUE) ~ "Arapoanga",
                            grepl("AGUA QUENTE", description, ignore.case = TRUE) ~ "Água Quente",
                            TRUE ~ "Outros"))  %>%
           # 'Outros' precisa ser filtrado, pois pode conter regiões, municípios fora do DF
           dplyr::filter(location != "Outros") %>% 
           dplyr::filter(property_type != "Outros")
  
  
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

