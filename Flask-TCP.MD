title Communications with admin front end

participantgroup Frontend:
participant E-mailPort
participant Interface
end
participantgroup Backend:
participant Flask
participantgroup Bottom backend:
participant TCPserver
participant Database
end
end 

loop Index.html
Interface -> Flask: GET index.html
Flask -> Interface: login.html
Interface -> Flask: POST form data;\n{"mail":"mail:haha@bugaga.com",\n"password":"plaintext"}
Flask -> TCPserver: Request user data:\n u/?mail:haha@bugaga.com
TCPserver->Database: db.admins.find_one\n({"mail":"haha@bugaga.com"})
Database->TCPserver: user data as json
note left of Database:{\n"mail":"haha@bugaga.com",\n"password":"hash",\n"doors":\n       [\n                {\n                  name: "Зеленый Квартал",\n                  id: "5544332211",\n                  picture: "link"\n                  enter: \n                            [\n                                        {\n                                        name: "1A", \n                                        picture: "link", \n                                        MAC: "80:e6:50:02:a3:9a"\n                                        }\n                            ]\n                 }\n        ]\n}
TCPserver->Flask: u/{user data as json}
Flask->Flask: Check hash
Flask->Interface:RETURN index.html
alt Forgot Password
Interface->Flask: GET forgotpass.html
Flask->E-mailPort: Send mail to:\nhaha@bugaga.com
E-mailPort-->>Interface:E-mail: go to url:forgotpass/verificationcode
E-mailPort->Flask: verificationcode
Interface->Flask: GET\nurl:forgotpass/verificationcode
Flask->Interface: RETURN forgotpass.html
Interface->Flask: POST form data;\n{"mail":"mail:haha@bugaga.com",\n"password":"plaintext"}
Flask->TCPserver: u/!mail:haha@bugaga.com;\npass:hash
TCPserver->Database: db.admins.insert_one\n({"mail":"haha@bugaga.com",\n"password":"hash+salt"})
Database->TCPserver: RETURN user
TCPserver->Flask: u/{user data as json}
Flask->Interface: RETURN index.html
end
end 

opt MyBuildings
Interface->Flask:GET mybuildings.html
Flask->TCPserver:u/?mail:haha@bugaga.com
TCPserver->Database:db.admins.find_one\n({"mail":"haha@bugaga.com"})
Database->TCPserver:user data
TCPserver->Flask:u/{user data as json}
Flask->Interface:Ninja loop\nRETURN mybuildings.html
opt Mybuilding: choose one specific building and show all users in that building
Interface->Flask:GET mybuilding.html
Flask->TCPserver:b/ID:5544332211;\nmail:haha@bugaga.com\n\nID of building and user mail
TCPserver->Database:db.users.find\n({"doors.id":"5544332211"})
Database->TCPserver:[{...},{...},...]
note left of Database:array of {\n"ID":id,\n"name":nameandsurname,\n"verification":"somecode",\n"phone":phone,\n"company":company,\n"position":position,\n"departament":departament,\n"doors":\n       [\n                {\n                  name: "Зеленый Квартал",\n                  id: "5544332211",\n                  picture: "link"\n                  enter: \n                            [\n                                        {\n                                        name: "1A", \n                                        picture: "link", \n                                        MAC: "80:e6:50:02:a3:9a"\n                                        }\n                            ]\n                 }\n        ]\n}
loop For each user of building
TCPserver->Database:db.log.find\n({"user_id":id})
Database->TCPserver:Log of each user
note left of Database:array of {\n"user_id":id,\n"door_id":MAC,\n"timestamp":timestamp\n}
end
note over TCPserver: Тут надо бы придумать...
end
end