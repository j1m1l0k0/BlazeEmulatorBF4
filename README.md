Blaze Emulator SQLiteV3 Support 
j1m1l0k0

English:
---------------------
I ported the BlazeEmulator Version to Support SQLite V3

The site below converts the SQL script file to SQLite3 format
https://www.rebasedata.com/convert-mysql-to-sqlite-online (just import the SQL into the site and wait for the migration)

Needed python libraries for the Blaze Emulator to work
command for installing libs.

Download Python -> https://www.python.org/downloads/release/python-2716/

python -m pip install twisted pyopenssl pysqlite3 service_identity

the database file should be changed in the Init.py file for your preference

*** Use the LoginGeneratorDB.py tool to create the user and password in the database to enter the game. ***

------------------------------------------------------------------------------------------------------------------------------

Brazilian Portuguese:
----------------------
Portei a Versão do BlazeEmulator para Suportar SQLite V3

O site abaixo faz a conversão do arquivo script SQL para formato SQLite3
https://www.rebasedata.com/convert-mysql-to-sqlite-online (basta importar o SQL no site e aguardar a migração)

Download Python -> https://www.python.org/downloads/release/python-2716/

Bibliotecas necessárias do python para o Blaze Emulador funcionar
comando para instalação das libs.

python -m pip install twisted pyopenssl pysqlite3 service_identity

o arquivo de banco de dados deverá ser alterado no arquivo Init.py para sua preferência

*** Use a ferramente LoginGeneratorDB.py para criar usuário e senha no banco de dados para entrar no jogo. ***
