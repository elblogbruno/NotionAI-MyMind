import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'api/api.dart';

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
          title: const Text('Notion AI My Mind Settings'),
        ),
        body: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
              children: <Widget>[
                TextField(
                  decoration: InputDecoration(
                    border: OutlineInputBorder(),
                    labelText: 'Server url (do not forget the / at the end)' ,
                    hintText: "http://xxx.xxx.x.xx:xxxx/",
                  ),
                  onChanged: (text) {
                    print("First text field: $text");
                  },
                  controller: myController,
                ),
                SizedBox(height: 50),
                Text(
                  "Current url: ",
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

              ]
          )
        ),
        floatingActionButton: FloatingActionButton(
          // When the user presses the button, show an alert dialog containing
          // the text that the user has entered into the text field.
          onPressed: () {
            return showDialog(
              context: context,
              builder: (context) {
                Api().setServerUrl(myController.text);
                Api().getServerUrl().then((val) => setState(() {
                  _textFromFile = val;
                }));
                return AlertDialog(
                  // Retrieve the text the that user has entered by using the
                  // TextEditingController.
                  title: Text("URL Saved: "),
                  content: Text(_textFromFile),
                );

              },
            );
          },
          tooltip: 'Save!',
          child: Icon(Icons.save),
        ),
      ),
    );


  }


}


