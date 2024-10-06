#' @title Desenvolvimento do front-end 
#' @author Luiz Paulo Tavares Gonçalves 

ui <- bslib::page_sidebar(
  
  title = "Observatório imobiliáro do Distrito Federal",
  shinyjs::useShinyjs(),
  
  # Definindo o tema
  
  theme = bslib::bs_theme(preset = "materia"),
  
  # Barra Lateral
  sidebar = HTML(paste0(
    "<br>",
    # "<a href='https://coinpaper.com/crypto-logos/bitcoin-logo' target='_blank'><img style='display: block; margin-left: auto; margin-right: auto;' src='https://res.coinpaper.com/coinpaper/bitcoin_btc_logo_e68b8dbb0c.svg' width='186'></a>",
    "<br>",
    "<p style='text-align: center;'><small><a href='https://www.linkedin.com/in/luiz-paulo-tavares-gon%C3%A7alves-611849174/' target='_blank'>Desenvolvido por Luiz Paulo Tavares</a></small></p>",
    "<br>",
    "<div class='d-flex justify-content-center'>",
    "  <a href='https://github.com/LuizPaulo23' target='_blank'>GitHub</a>",
    "  <a href='https://www.instagram.com/luiz_paulo.023/' target='_blank'>Instagram</a>",
    "</div>",
    "<br>"
  )),
  
  # Corpo do Dashboard
  
  dashboardBody(
    
    # tags$p("Última atualização: ", Sys.Date(), style = "color:black;"),
    
    # Tabset para as seções
    
    tabsetPanel(
      tabPanel("Preço Geral",
               box(title = "Preço de Venda", status = "info", solidHeader = TRUE, width = 12,
                   plotOutput("histogramPlot"))
      ),
      tabPanel("Regiões do DF",
               box(status = "info", solidHeader = TRUE, width = 12,
                   selectInput("property_type", "Selecione o Tipo de Imóvel:", 
                               choices = c("Apartamento", "Casa", "Casa Condominio")),
                   plotOutput("regionPlot")
               )
      )
    )
  )
)

