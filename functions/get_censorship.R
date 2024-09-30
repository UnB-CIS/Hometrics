get_censorship <- function(){
  
  n <- nrow(data_raw) * 0.05
  
  ordenado <- data_raw %>% 
    dplyr::arrange(price) %>% 
    dplyr::slice(1601:(n() - 1600))
  
  
}