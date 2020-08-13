import 'package:flutter/material.dart';
import 'package:notion_ai_my_mind/bottom-app-bar.dart';
import 'package:notion_ai_my_mind/color_palette.dart';



void main() => runApp(new MyApp());

class MyApp extends StatelessWidget {
  // This widget is the root of your application.
  @override
  Widget build(BuildContext context) {
    return new MaterialApp(
      title: 'Flutter Demo',
      theme: new ThemeData(
        // This is the theme of your application.
        //
        // Try running your application with "flutter run". You'll see the
        // application has a blue toolbar. Then, without quitting the app, try
        // changing the primarySwatch below to Colors.green and then invoke
        // "hot reload" (press "r" in the console where you ran "flutter run",
        // or press Run > Flutter Hot Reload in IntelliJ). Notice that the
        // counter didn't reset back to zero; the application is not restarted.
        primarySwatch: generateMaterialColor(Palette.primary),
        //primaryColor: Colors.red,
        //backgroundColor: Colors.white,
        //bottomAppBarColor: Colors.white,
      ),
      home: new MyHomePage(title: 'BottomAppBar with FAB'),
    );
  }
}
class Palette {
  static const Color primary = Color(0xFFFF5F5F);
}
class MyHomePage extends StatefulWidget {
  MyHomePage({Key key, this.title}) : super(key: key);

  final String title;

  @override
  _MyHomePageState createState() => new _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> with TickerProviderStateMixin {
  String _lastSelected = 'TAB: 0';

  final globalKey = GlobalKey<ScaffoldState>();
  void _selectedTab(int index) {
    setState(() {
      _lastSelected = 'TAB: $index';
    });
  }


  @override
  Widget build(BuildContext context) {
    return Scaffold(
      key: globalKey,
      extendBody: true,
      appBar: AppBar(
        title: Text(widget.title),
      ),
      body: Center(
        child: Text(
          _lastSelected,
          style: TextStyle(fontSize: 32.0),
        ),
      ),
      bottomNavigationBar: FABBottomAppBar(
        backgroundColor: Colors.white,
        centerItemText: ' ',
        color: Colors.grey,
        selectedColor: Colors.red,
        notchedShape: CircularNotchedRectangle(),
        onTabSelected: _selectedTab,
        items: [
          FABBottomAppBarItem(iconData: Icons.person_outline, text: ''),
          //FABBottomAppBarItem(iconData: Icons.layers, text: 'Is'),
          FABBottomAppBarItem(iconData: Icons.notifications_none, text: ''),
          //FABBottomAppBarItem(iconData: Icons.info, text: 'Bar'),
        ],
      ),

      floatingActionButtonLocation: FloatingActionButtonLocation.centerFloat,
      floatingActionButton: _buildFab(
          context), // This trailing comma makes auto-formatting nicer for build methods.
    );
  }

  Widget _buildFab(BuildContext context) {
    /*final icons = [ Icons.sms, Icons.mail, Icons.phone ];
    return AnchoredOverlay(
      showOverlay: false,
      overlayBuilder: (context, offset) {
        return CenterAbout(
          position: Offset(offset.dx, offset.dy - icons.length * 35.0),
          child: FabWithIcons(
            icons: icons,
            onIconTapped: _selectedFab,
          ),
        );
      },
      child: FloatingActionButton(
        onPressed: () { },
        tooltip: 'Increment',
        child: Icon(Icons.home),
        elevation: 3.0,
      ),
    );*
    return new FloatingActionButton(
        onPressed: () {
          final snackBar = SnackBar(
            content: Text('Yay! A SnackBar!'),
            action: SnackBarAction(
              label: 'Undo',
              onPressed: () {
                // Algo de código para ¡deshacer el cambio!
              },
            ),
          );

          // Encuentra el Scaffold en el árbol de widgets y ¡úsalo para mostrar un SnackBar!
          Scaffold.of(context).showSnackBar(snackBar);
        },
        tooltip: 'Increment',
        child: Icon(Icons.home),
        focusColor: Colors.red,
        elevation: 10.0,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.all(Radius.circular(16.0))),
    );
  }*/
    return new Container(
      padding: EdgeInsets.only(bottom: 5.0),
      child: Align(
        alignment: Alignment.bottomCenter,
        child: FloatingActionButton(
        onPressed: () {
              final snackBar = SnackBar(
              content: Text('Yay! A SnackBar!'),
              action: SnackBarAction(
              label: 'Undo',
              onPressed: () {
              // Algo de código para ¡deshacer el cambio!
              },
              ),
              );

              // Encuentra el Scaffold en el árbol de widgets y ¡úsalo para mostrar un SnackBar!
              globalKey.currentState.showSnackBar(snackBar);
        },
        tooltip: 'Increment',
        child: Icon(Icons.home),
        focusColor: Colors.red,
        elevation: 3.0,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.all(Radius.circular(16.0))),
            ),
          ),
    );
  }
}