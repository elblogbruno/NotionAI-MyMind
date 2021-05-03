import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:notion_ai_my_mind/qrcode.dart';
import 'package:notion_ai_my_mind/resources/strings.dart';
import 'api/api.dart';
import 'locales/main.i18n.dart';

class settings extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return new settingsPage();
  }
}
class settingsPage extends StatefulWidget {
  @override
  settingsState createState() => settingsState();
}
class settingsState extends State<settingsPage> {
  final myController = TextEditingController();
  String _textFromFile = "";

  @override
  void dispose() {
    // Clean up the controller when the widget is disposed.
    myController.dispose();
    super.dispose();
  }

  settingsState() {
    Api().getServerUrl().then((val) => setState(() {
      _textFromFile = val;
    }));
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      theme: ThemeData(primarySwatch: Colors.teal, accentColor: Color(0xFFDD5237)),
      home: Scaffold(
        appBar: AppBar(
          title:  Text(Strings.settingsTitle.i18n),
        ),
        body: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
              children: <Widget>[
                TextField(
                  decoration: InputDecoration(
                    border: OutlineInputBorder(),
                    labelText: Strings.settingsHint.i18n,
                    hintText: "http://xxx.xxx.x.xx:xxxx/",
                  ),
                  controller: myController,
                ),
                SizedBox(height: 50),
                Text(
                  Strings.actualUrlHint.i18n,
                  textAlign: TextAlign.center,
                  overflow: TextOverflow.ellipsis,
                  style: TextStyle(fontWeight: FontWeight.bold,fontSize: 35),
                ),
                SizedBox(height: 20),
                Text(
                    _textFromFile,
                    textAlign: TextAlign.center,
                    overflow: TextOverflow.ellipsis,
                    style: TextStyle(fontWeight: FontWeight.bold,fontSize: 20),
                ),
                SizedBox(height: 20),
                ElevatedButton(
                  onPressed: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(builder: (context) => QRViewExample()),
                    );
                  },
                  style: ElevatedButton.styleFrom(
                    primary: Colors.teal,
                  ),
                  child:  Icon(
                    Icons.qr_code,
                    color: Colors.white,
                    size: 50,
                  ),
                ),
              ]
          )
        ),
        floatingActionButton: FloatingActionButton(
          // When the user presses the button, show an alert dialog containing
          // the text that the user has entered into the text field.
          onPressed: () {
            Api().setServerUrl(myController.text);
            showDialog(context: context, builder: (x) => _ShowAlert(context));
          },
          tooltip: 'Save!',
          child: Icon(Icons.save),
        ),
      ),
    );
  }
  Widget _ShowAlert(BuildContext context) {
    return FutureBuilder<String>(
        future:  Api().getServerUrl(), // a previously-obtained Future<String> or null
        builder: (BuildContext context, AsyncSnapshot<String> snapshot) {
          List<Widget> children;
          if (snapshot.hasData) {
            final dialog = AlertDialog(
              // Retrieve the text the that user has entered by using the
              // TextEditingController.
              title: Text("URL Saved: "),
              content: Text(snapshot.data),
            );
            return dialog;
          } else if (snapshot.hasError) {
            final dialog = AlertDialog(
              // Retrieve the text the that user has entered by using the
              // TextEditingController.
              title: Text("URL Not Saved: "),
              content: Text(snapshot.error),
            );
            return dialog;
          } else {
            children = <Widget>[
              SizedBox(
                child: CircularProgressIndicator(),
                width: 60,
                height: 60,
              )
            ];
          }
          return Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              crossAxisAlignment: CrossAxisAlignment.center,
              children: children,
            ),
          );
        });
  }

}


