title Communications with admin front end

participantgroup Frontend:
participant Interface
end
participantgroup Backend:
participant Flask
participant TCPserver
participant Database
participant E-mailPort
end 

loop Index.html
Interface -> Flask: GET index.html
Flask -> Interface: login.html
Interface -> Flask: POST form data;\n{"mail":"mail:haha@bugaga.com",\n"password":"hash"}
Flask -> TCPserver: Request user data:\n u/?mail:haha@bugaga.com
TCPserver->Database: db.admins.find_one\n({"mail":"haha@bugaga.com"})
Database->TCPserver: {"mail":"haha@bugaga.com",\n"password":"hash"}
note left of Database:{\n"mail":"haha@bugaga.com",\n"password":"hash",\n"doors":[...]\n}
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
Interface->Flask: POST form data;\n{"mail":"mail:haha@bugaga.com",\n"password":"hash"}
Flask->TCPserver: u/!mail:haha@bugaga.com;\npass:hash
TCPserver->Database: db.admins.insert_one\n({"mail":"haha@bugaga.com",\n"password":"hash"})
Database->TCPserver: RETURN user
TCPserver->Flask: u/!mail:haha@bugaga.com;\npass:hash
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
opt Mybuilding: can be choosen all
Interface->Flask:GET mybuilding.html
Flask->TCPserver:b/ID:5544332211\nID of building
TCPserver->Database:db.doors.find\n({"parent_id":"5544332211"})
Database->TCPserver:[{...},{...},...]
note left of Database:{\n"name":"A1",\n"ID":"80:e6:50:02:a3:9a",\n"password":"blabla",\n"ttl":"123124123",\n"parent_id":"5544332211",\n"parent_zone_id":"80:e6:50:02:a3:9b",\n"picture":"img/pic1.png"\n}
TCPserver->Flask:b/[{...},{...},...]
Flask->Interface:RETURN mybuilding.html\nList of users with data

end
end