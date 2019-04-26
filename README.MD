BuyQawHub
===

BuyQawHub is the hybrid mobile app (java script based) that controls door controllers and communicates with TCP socket server.

# Table of Contents

[TOC]

# Functionality

1. Open doors controlled by BLE controllers by the specific algorithm shown in the sequence diagram. In simple words:
    1. Mobile app acts like peripheral BLE device.
    2. When controller connects to it, it acts like BLE server with special services and characteristics.
    3. Controller sends its MAC address
    4. Mobile app takes value of locally stored password and shows password to the controller by notifying it
    5. Controller says that password is OK
    6. Mobile app says open the door
2. Connect and communicate with TCP Socket server:
    1. Connect to the server and update passwords and user information
    2. Send usage data to the server
    3. Every 15 minutes update
3. Show data to the user and interact with him:
    1. Collect data from forms
    2. Show data in pages
    3. Send notifications

## Communications with controller

Mobile app communicates with controller by Bluetooth Low Energy protocol. 

:::info
It can be used in hybrid development by [cordova-plugin-ble-peripheral](https://github.com/don/cordova-plugin-ble-peripheral) plugin.
:::

### Simple code

This fiddle creates BLE peripheral at device ready and waits to smb connection and write to `RX_UUID`.

```javascript=
// Nordic UART Service
var SERVICE_UUID = '00FF';
var TX_UUID = '00F0';
var RX_UUID = '00F1';
var update = []


var app = {
    // Application Constructor
    initialize: function() {
        this.bindEvents();
    },
    bindEvents: function() {
        document.addEventListener('deviceready', this.onDeviceReady, false);
        sendButton.addEventListener('touchstart', this.updateCharacteristicValue, false);
    },
    onDeviceReady: function() {

        var property = blePeripheral.properties;
        var permission = blePeripheral.permissions;

        blePeripheral.onWriteRequest(app.didReceiveWriteRequest);
        blePeripheral.onBluetoothStateChange(app.onBluetoothStateChange);

        // 2 different ways to create the service: API calls or JSON
        app.createService();

    },
    createService: function() {
        // https://learn.adafruit.com/introducing-the-adafruit-bluefruit-le-uart-friend/uart-service
        // Characteristic names are assigned from the point of view of the Central device

        var property = blePeripheral.properties;
        var permission = blePeripheral.permissions;

        Promise.all([
            blePeripheral.createService(SERVICE_UUID),
            blePeripheral.addCharacteristic(SERVICE_UUID, TX_UUID, property.WRITE, permission.WRITEABLE),
            blePeripheral.addCharacteristic(SERVICE_UUID, RX_UUID, property.READ | property.NOTIFY, permission.READABLE),
            blePeripheral.publishService(SERVICE_UUID),
            blePeripheral.startAdvertising(SERVICE_UUID, 'UART')
        ]).then(
            function() { console.log ('Created UART Service'); },
            app.onError
        );

        blePeripheral.onWriteRequest(app.didReceiveWriteRequest);
    },
    

        Promise.all([
            blePeripheral.createServiceFromJSON(uartService),
            blePeripheral.startAdvertising(uartService.uuid, 'UART')
        ]).then(
            function() { outputDiv.innerHTML = 'Вкл.'; },
            app.onError
        );
    },
    updateCharacteristicValue: function() {
        var input = '1';
        var bytes = stringToBytes(input.value);

        var success = function() {
            outputDiv.innerHTML += messageInput.value + '<br/>';
            console.log('Updated RX value to ' + input.value);
        };
        var failure = function() {
            console.log('Error updating RX value.');
        };

        blePeripheral.setCharacteristicValue(SERVICE_UUID, RX_UUID, bytes).
            then(success, failure);

    },
    didReceiveWriteRequest: function(request) {
        var message = bytesToString(request.value);
        console.log(message);
        if(message!="0"){
          // var today = new Date();
          // var time = today.getHours() + ":" + today.getMinutes();
          // update[update.length] = {"text": "Вы зашли в ЗК", "img": "img/zk.jpg", "time": time};
          // UpdateTable(update);
          rps();
        }
    },
    onBluetoothStateChange: function(state) {
        console.log('Bluetooth State is', state);
        if(state == "off"){
          outputDiv.innerHTML = 'Выкл.';
        }

    }
};

app.initialize();
```

## Communication with TCP socket server

Communication with TCP socket server goes through TCP socket (thanks, cap!) by the internet connection.

Mobile need to connect to static ip and port and update status with it.

:::warning
Strings inside the socket has to decoded and encoded to and from `UTF-8` coding.
:::

### Protocol

Protocol is shown in the sequence diagram, here goes some examples:

1. Registration:
    1. `r/56303h43;name and surname;phone;position;dep;company;`
    2. `r/` - every first letter is control variable, this one means `registration`
    3. `56303h43` - ID number of user
    4. and so on


## Design

Design of the mobile app is prepared and prototype can be found [here](https://www.figma.com/file/GJO1zLYeHgWTXUN8KfI7VAUT/BuyQawHub), as a reference theme was used [this one](https://www.enableds.com/products/apptastic/homepages.html).

### Pages

#### Verification page
In this page user enters verification code from invite to start registration process.
![](https://i.imgur.com/xC521D3.jpg)

#### Sign up
Here user fills out the registration form, all of them are required.
![](https://i.imgur.com/m8AqLhQ.png)


#### Home page with enabled service
It is the home page of the mobile app with enabled service. Big picture is button.
![](https://i.imgur.com/Sa4IDQd.png)

#### Home page with disabled service
Home page with disabled service. When button is pressed - bluetooth is turned on.

![](https://i.imgur.com/9HNqYjB.png)

#### Menu
When 4 squares at the right top corner is clicked, menu shows.

![](https://i.imgur.com/7w217t5.png)

#### Buildings page
Building pages is taken from array of dictionaries send from the server. When building is pressed - go to page zones.

![](https://i.imgur.com/1nskT38.png)

#### Zones page
This page shows enabled for this user zones inside the building. They can be with pictures or not.

![](https://i.imgur.com/XHIEdsX.png)

#### Messages page

Messages page is archive of unread notifications form the server. They sent in structure:
`m/utf-8 font awesome icon;hex color;title;full text;`

On message pressed Message page is shown.

![](https://i.imgur.com/J6wdXtk.png)

#### Message
Full text of the message page.

![](https://i.imgur.com/SLEiMvI.png)

#### Settings page
Links to 4 pages.

![](https://i.imgur.com/AqF7kLG.png)

#### Terms of service and About us
Links to the web pages.

#### Invite guest
Here user can invite guest. More info in Invite Guest box in Sequences.

![](https://i.imgur.com/aiw3C5e.png)

#### How to
Slideshow that appears at the very beginning of the app.

![](https://i.imgur.com/NNYf32b.png)


#### Profile change
Page to change profile. Profile change has to be accepted form the server, so it will not change instantly. More info in sequence diagram.

![](https://i.imgur.com/TttoVCL.png)


## Sequence diagram

![](https://i.imgur.com/OZzPbZm.png)


### Sequence diagram code


You can copy and paste it [here](https://sequencediagram.org/).

```
title BuyQawHub


participant TCPServer
participant MobileApp
participant Controller
fontawesome f2c6 Outside #1da1f2
fontawesome f187 AppStore #1da102

loop Door opening
MobileApp-->Controller: Advertize BLE peripheral
note over MobileApp: Characteristics of \nthe ble peripheral is:\n1. Service UUID = "BA10"\n2. CHECK_UUID = "BA52" Checking [WRITE]\n3. PASSWD_PORT_UUID = "BA44" Enter password [NOTIFY]\n4. ADMIN_PORT_UUID = "BA13" Admin settings [NOTIFY]\n5. ACTION_PORT_UUID = "BA87" Give order [NOTIFY]\n6. INCOMING_PORT_UUID = "BA76" Input for controller [WRITE]\n7. FILLER_0 = "BA66" Non coding filler [NOTIFY]\n8. FILLER_1 = "BA91" Non coding filler [NOTIFY]\n9. FILLER_2 = "BA01" Non coding filler [NOTIFY]\n10. FILLER_3 = "BA28" Non coding filler [NOTIFY]
Controller-->MobileApp: Connect
note left of Controller: When user is near door with\ncontoller, controller connects\nto ble peripheral in mobile\napp and sends mac address\nto it in form:\n80:e6:50:02:a3:9a 
Controller->MobileApp: Write to CHECK_UUID:\n 80:e6:50:02:a3:9a
MobileApp->MobileApp: Check local storage
alt No password in local storage
MobileApp->TCPServer: a/?56303h43;80:e6:50:02:a3:9a;
note left of MobileApp: 1. a/? - control letter, means\n"Asking password"\n2.56303h43 - id of user, given\nat registration\n3. 80:e6:50:02:a3:9a - MAC \nadress of Controller
TCPServer->MobileApp: a/123456;1555666261;
note right of TCPServer: 1. a/ - control letter, means\n"Answer is"\n2.123456 - password\n3. 1555666261 - Timestamp\nof time to live of this password
alt No access
TCPServer->MobileApp: a/0;0;
MobileApp->TCPServer: a/!0;0;
end
end
MobileApp->Controller:PASSWD_PORT_UUID as NOTIFY:\n123456
Controller->MobileApp: INCOMING_PORT_UUID:\n1
opt Password change
MobileApp->TCPServer:e/?80:e6:50:02:a3:9a
TCPServer->MobileApp:e/654321
alt No change
TCPServer->MobileApp:e/!
MobileApp->TCPServer:e/!
end
MobileApp->Controller:ADMIN_PORT_UUID as NOTIFY:\n654321
Controller->MobileApp:INCOMING_PORT_UUID:\n654321
end
MobileApp->Controller: ACTION_PORT_UUID as NOTIFY:\n1\n[It means open the door]
Controller->MobileApp:INCOMING_PORT_UUID:\n1\n[Done]
Controller-->MobileApp: Disconnect
MobileApp->TCPServer:a/!56303h43;80:e6:50:02:a3:9a;1555666261;
note left of MobileApp: 1. a/! - control letter\n2. 56303h43 - ID of user\n3. 80:e6:50:02:a3:9a - MAC adress\nof Controller\n4. 1555666261 - Timestamp, when\nuser opened door
TCPServer->MobileApp:a/!
end

opt User registration
MobileApp->TCPServer: Verification code:\nv/GG89#!tgh77
TCPServer->MobileApp: User ID:\nv/56303h43
alt Bad verification code
TCPServer->MobileApp: v/0
end 
MobileApp->TCPServer: Form details from Sign Up page:\nr/56303h43;name and surname;phone;position;dep;company;
TCPServer->MobileApp: List of buildings and enters:\nr/[{name: "Зеленый Квартал", id: "5544332211",picture: "link"\nenter: [{name: "1A", ttl: "1555666261", key: "123456", picture: "link", MAC: "80:e6:50:02:a3:9a"}]}]
end
opt Profile update
MobileApp->TCPServer:Data from form in Profile page:\nr/56303h43;name and surname;phone;position;dep;company;
TCPServer->MobileApp:Ok, wait for answer in messages box:\nr/!
end
opt Messages
MobileApp->TCPServer:Every 15 minutes:\nm/?
TCPServer->MobileApp:If no messages:\nm/0\nIf any:\nm/utf-8 font awesome icon;hex color;title;full text;
alt Profile change message
TCPServer->MobileApp: New profile data:\nr/56303h43;name and surname;phone;position;dep;company;\n[{name: "Зеленый Квартал", id: "5544332211",picture: "link"\nenter: [{name: "1A", ttl: "1555666261", key: "123456", picture: "link", MAC: "80:e6:50:02:a3:9a"}]}]
end
end
opt Invite Guest
MobileApp->TCPServer: Data from Invite Guest page:\ng/?56303h43;[{id: "5544332211", enter: [{name: "1A", MAC: "80:e6:50:02:a3:9a"}]}]; ttl:"1555666261"
TCPServer->MobileApp: Verification code:\n2178969124hn#123
MobileApp->Outside: Share by deep link:\nbuyqawhub:/ /2178969124hn#123
end
opt Be Guest
Outside->MobileApp: Deep link with verification code
MobileApp->TCPServer: g/!56303h43;2178969124hn#123;
TCPServer->MobileApp: r/56303h43;name and surname;phone;position;dep;company;\n[{name: "Зеленый Квартал", id: "5544332211",picture: "link"\nenter: [{name: "1A", ttl: "1555666261", key: "123456", picture: "link", MAC: "80:e6:50:02:a3:9a"}]}]
alt App is not installed
Outside->AppStore: Install mobile app
AppStore->MobileApp: Put verification code
ref over MobileApp: Registration process
end
end
```

# Useful links
1. [BLE peripheral cordova plugin](https://github.com/don/cordova-plugin-ble-peripheral)
2. [How BLE works](https://www.mikroe.com/blog/bluetooth-low-energy-part-1-introduction-ble)
3. [What is Service and Characteristic in BLE](https://www.oreilly.com/library/view/getting-started-with/9781491900550/ch04.html)
4. [Mobile app to simulate door](https://play.google.com/store/apps/details?id=no.nordicsemi.android.mcp)
5. [Mini tutorial howtoNrfConnect](https://youtu.be/sGrBiuT3AlM)