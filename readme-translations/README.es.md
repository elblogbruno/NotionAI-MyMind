<!-- PROJECT LOGO -->
<br />
<p align="center">
  <a href="https://github.com/elblogbruno/NotionAI-MyMind/">
    <img src="Chrome%20and%20Firefox%20Extension/icon/icon.png" alt="Logo" width="80" height="80">
  </a>

  <h3 align="center">NotionAI MyMind</h3>

  <p align="center">
    Este repo utiliza la IA y el maravilloso Notion para permitirte añadir cualquier cosa de la web a tu "Mente" y olvidarte de todo lo demás.
    <br />
    <a href="https://github.com/elblogbruno/NotionAI-MyMind/wiki"><strong>Explorar la documentación »</strong></a>
    <br />
    <br />
    <a href="https://www.notion.so/glassear/My-Mind-Demo-Structure-ebd913d0cfa14889b122d391a883db94">Ver demostración</a>
    ·
    <a href="https://github.com/elblogbruno/NotionAI-MyMind/issues">Informar de un error</a>
    ·
    <a href="https://github.com/elblogbruno/NotionAI-MyMind/discussions/categories/ideas">Solicitar una función</a>
  </p>
  <p align="center">
    <a href='https://chrome.google.com/webstore/detail/notion-ai-my-mind/eaheecglpekjjlegffodbfhbhdmnjaph?hl=es&authuser=0 '><img align="center" style="overflow: hidden; display: inline-block;" alt='Get it on Chrome Web Store' width=200          height=60 src='https://storage.googleapis.com/chrome-gcs-uploader.appspot.com/image/WlD8wC6g8khYWPJUsQceQkhXSlv1/HRs9MPufa1J1h5glNhut.png'/></a>  <a href='https://addons.mozilla.org/en-US/firefox/addon/notion-ai-my-mind/'><img align="center" style="overflow: hidden; display: inline-block;" alt='Get it on Firefox Add-On Store' width=172 height=60  src='https://ffp4g1ylyit3jdyti1hqcvtb-wpengine.netdna-ssl.com/addons/files/2015/11/get-the-addon.png'/></a>  <a href='https://play.google.com/store/apps/details?id=com.elblogbruno.notion_ai_my_mind&pcampaignid=pcampaignidMKT-Other-global-all-co-prtnr-py-PartBadge-Mar2515-1'><img align="center" style=" overflow: hidden; display: inline-block;" alt='Get it on Google Play' width=250 height=100 src='https://play.google.com/intl/en_us/badges/static/images/badges/en_badge_web_generic.png'/></a>
  
  </p>
</p>

### Añadir contenido 
<a href="https://github.com/elblogbruno/NotionAI-MyMind/wiki/Notion-AI-My-Mind-Collections"><strong>Este es el ejemplo de las colecciones, donde se pueden tener diferentes colecciones o bases de datos de contenidos, totalmente personalizables en Notion. »</strong></a>

<a href="https://github.com/elblogbruno/NotionAI-MyMind/wiki/Notion-AI-My-Mind-Collections">
    <img src="doc/header_collections_example_modify_title_tags.gif" alt="collections" width="690" height="388">
    <img src="doc/header_phone_demo.gif" alt="collections" height="388">
 </a>

### Buscar en
<a href="https://www.notion.so/Intro-to-databases-fd8cd2d212f74c50954c11086d85997e"><strong>Se trata de una base de datos totalmente personalizable y con capacidad de búsqueda en Notion. »</strong></a>

<a href="https://www.notion.so/Intro-to-databases-fd8cd2d212f74c50954c11086d85997e">
    <img src="doc/header_gif_search.gif" alt="collections" width="690" height="388">
 </a>
 
# ¡Libera tu mente!

<!-- TABLE OF CONTENTS -->
<details open="open">
  <summary>Índice de contenidos</summary>
  <ol>
    <li>
      <a href="#project-philosophy">Filosofía del proyecto</a>
      <ul>
        <li><a href="#examples-of-what-you-can-do">Ejemplos</a></li>
        <li><a href="#extensions">Extensiones de la mente</a></li>
      </ul>
    </li>
    <li>
      <a href="#installing">Instalación</a>
      <ul>
        <li><a href="#i-have-installed-the-server-what-to-do-next">He instalado el servidor, ¿qué hacer a continuación?</a></li>
        <li><a href="#docker-compose">Docker-Compose</a></li>
       </ul>
      </ul>
    </li>
    <li><a href="#common-issues">Problemas comunes</a></li>
    <li><a href="#roadmap">Hoja de ruta</a></li>
  </ol>
</details>

## Filosofía del proyecto.

La idea es tener extensiones para tu mente en el navegador, y aplicación en android e Ios, permitiéndote añadir cualquier cosa que encuentres en la web en tu "Mente". También, añadir capacidades de etiquetado de imágenes y artículos gracias a la IA, para que puedas simplemente buscar en tu "Mente" lo que recuerdes.

En este momento, hay un servidor local de Python en funcionamiento, que recibe todos los datos de la extensión y la aplicación, y los publica en su base de datos totalmente personalizable y con capacidad de búsqueda en Notion. ¡Así que es 100% de código abierto y totalmente privado!

¡Tal vez podemos decir que es una alternativa de código abierto a [Raindrop](https://raindrop.io/) y [Microsoft Edge Collections](https://support.microsoft.com/en-us/microsoft-edge/organize-your-ideas-with-collections-in-microsoft-edge-60fd7bba-6cfd-00b9-3787-b197231b507e), pero mucho más fresco con la opinión de la comunidad y las capacidades que ofrece la Inteligencia Artificial, y un desarrollador con mucha imaginación (sí, mi cerebro va a 150% de velocidad)!

## Ejemplos de lo que puedes hacer.

Añade texto a tu mente   |  Añade imágenes a tu mente
:---: | :---:
![](doc/add_text.gif)  |  ![](doc/add_image.gif)


Añade sitios web a tu mente |  Busca en tu mente
:---: | :---:
![](doc/add_website.gif)  |  ![](doc/header_gif_search.gif)

### Extensiones de la mente
### Chromium users
¡Los navegadores basados en chromium como Google Chrome,Brave o Microsoft edge entre otros, pueden instalar la extensión desde la tienda!

<a href='https://chrome.google.com/webstore/detail/notion-ai-my-mind/eaheecglpekjjlegffodbfhbhdmnjaph?hl=es&authuser=0 '><img alt='Get it on Chrome Web Store' width=200 height=60 src='https://storage.googleapis.com/chrome-gcs-uploader.appspot.com/image/WlD8wC6g8khYWPJUsQceQkhXSlv1/HRs9MPufa1J1h5glNhut.png'/></a>

### Usuarios de Firefox
Los usuarios de Firefox pueden instalar la extensión desde la tienda.

<a href='https://addons.mozilla.org/en-US/firefox/addon/notion-ai-my-mind/'><img alt='Get it on Firefox Add-On Store' width=172 height=60 src='https://ffp4g1ylyit3jdyti1hqcvtb-wpengine.netdna-ssl.com/addons/files/2015/11/get-the-addon.png'/></a>

### Usuarios de Android e Ios

Los usuarios pueden instalar la aplicación para Android desde la tienda de Android. En Ios se puede clonar el proyecto flutter y construir la aplicación.

<a href='https://play.google.com/store/apps/details?id=com.elblogbruno.notion_ai_my_mind&pcampaignid=pcampaignidMKT-Other-global-all-co-prtnr-py-PartBadge-Mar2515-1'><img alt='Get it on Google Play' width=250 height=100 src='https://play.google.com/intl/en_us/badges/static/images/badges/en_badge_web_generic.png'/></a>


No voy a publicar la aplicación en la App Store de Apple, ya que no tengo una cuenta de desarrollador de Apple ni un ordenador basado en Mac OS.
Mientras tanto, puedes clonar el proyecto Flutter y construir la aplicación tú mismo.

## Tutorial de instalación
[![Tutorial de instalación](https://img.youtube.com/vi/v2wWtCYED1U/0.jpg)](https://www.youtube.com/watch?v=v2wWtCYED1U)

# Instalación
- Es muy fácil, y hay diferentes formas, desde las de click to install hasta las más avanzadas, en caso de que quieras instalarlo desde el código fuente.

- Puedes comprobarlo en la wiki: [Instalación del servidor de Notion AI My Mind](https://github.com/elblogbruno/NotionAI-MyMind/wiki/Installing-the-Notion-AI-My-Mind-Server)

- Esto cubre:
    - Instalación del servidor Notion AI My Mind. 

### He instalado el servidor, ¿qué hacer a continuación?
- Si no introduces las credenciales de Notion ni creas tu primera pagina en Notion, ¡no estaras disfrutando de todo esto!

- Puedes comprobarlo en la wiki: [He instalado el servidor, ¿qué hacer a continuación?](https://github.com/elblogbruno/NotionAI-MyMind/wiki/I-have-installed-the-server,-what-to-do-next%3F)

- Esto cubre:
    - Creación de la base de datos de Notion
    - Paseo por el navegador o la aplicación con explicaciones.
    - Creación de la estructura de tu mente con las distintas colecciones dentro.

- También puedes ver el vídeo sobre cómo crear la estructura de tu mente.
 
[![Tutorial de instalación](https://img.youtube.com/vi/sRn6Pk1PnSY/0.jpg)](https://www.youtube.com/watch?v=sRn6Pk1PnSY)

### Docker-Compose

- Puedes comprobarlo en la wiki: [Instalación del servidor de Notion AI My Mind en Docker](https://github.com/elblogbruno/NotionAI-MyMind/wiki/Installing-the-Notion-AI-My-Mind-Server-on-Docker)

- Esto cubre:
    - La instalación del servidor como una imagen Docker

## Problemas comunes

- Puedes comprobarlo en la wiki: [Problemas comunes](https://github.com/elblogbruno/NotionAI-MyMind/wiki/Common-Issues)

## Hoja de ruta
- Puede consultar la hoja de ruta aquí: https://github.com/elblogbruno/NotionAI-MyMind/projects/1
