import 'dart:async';
import 'dart:ui';

import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:fluttertoast/fluttertoast.dart';
import 'package:notion_ai_my_mind/Arguments.dart';
import 'package:notion_ai_my_mind/list_view.dart';

import 'package:notion_ai_my_mind/overlay_view.dart';
import 'package:notion_ai_my_mind/resources/strings.dart';
import 'package:notion_ai_my_mind/settings.dart';
import 'package:notion_ai_my_mind/tutorial_steps.dart';
import 'package:receive_sharing_intent/receive_sharing_intent.dart';

import 'package:notion_ai_my_mind/api/api.dart';
import 'package:tutorial/tutorial.dart';

final GlobalKey<NavigatorState> navigatorKey = new GlobalKey<NavigatorState>();

final keyOpenMindButton = GlobalKey();
final keyOpenServerButton = GlobalKey();
final keyRefreshCollections = GlobalKey();
final keySettings = GlobalKey();

bool isSharing = false;

Future<void> main() async {
  runApp(
    MaterialApp(
      navigatorKey: navigatorKey,
      theme: ThemeData(primarySwatch: Colors.teal, accentColor: Color(0xFFDD5237)),
      home: MyHomePage(),
      routes: {
        '/add': (BuildContext context) => AddLinkPage(),
      },
    ),
  );
}


class MyHomePage extends StatefulWidget {
    @override
    _MyAppState createState() => _MyAppState();
}

class _MyAppState extends State<MyHomePage> with WidgetsBindingObserver {
  StreamSubscription _intentDataStreamSubscription;
  List<SharedMediaFile> _sharedFiles;
  String _sharedText;
  List<TutorialItens> itens = [];

  @override
  void initState() {
    super.initState();
    _initShareIntent();
    itens = Tutorial_Steps().initTutorialItems(keyOpenMindButton,keySettings,keyRefreshCollections,keyOpenServerButton);
    WidgetsBinding.instance.addObserver(this);
  }

  void _initShareIntent() {
    // For sharing images coming from outside the app while the app is in the memory
    _intentDataStreamSubscription = ReceiveSharingIntent.getMediaStream()
        .listen((List<SharedMediaFile> value) {

      setState(() {
        _sharedFiles = value;
        isSharing = true;
      });

      if(_sharedFiles != null) {
        String uri = (_sharedFiles?.map((f) => f.path)?.join(",") ?? "");
        if (uri != null) {
          showListOfCollections(context,true, uri);
          //navigatorKey.currentState.pushNamed(CollectionListPage.routeName, arguments: Arguments(uri,true,0,navigatorKey));
        }
      }

      setState(() {
        _sharedFiles = null;
        isSharing = true;
      });

    }, onError: (err) {
      print("getIntentDataStream error: $err");
    });

    // For sharing images coming from outside the app while the app is closed
    ReceiveSharingIntent.getInitialMedia().then((List<SharedMediaFile> value) {
      setState(() {
        _sharedFiles = value;
        isSharing = false;
      });

      if(_sharedFiles != null) {
        String uri = (_sharedFiles?.map((f) => f.path)?.join(",") ?? "");

        if (uri != null) {

          showListOfCollections(context,true, uri);
          //navigatorKey.currentState.pushNamed(CollectionListPage.routeName, arguments: Arguments(uri,true,0,navigatorKey));
        }
      }

      setState(() {
        _sharedFiles = null;
        isSharing = false;
      });

    });

    // For sharing or opening urls/text coming from outside the app while the app is in the memory
    _intentDataStreamSubscription =
        ReceiveSharingIntent.getTextStream().listen((String value) {
          setState(() {
            _sharedText = value;
            isSharing = true;
          });

          if(_sharedText != null) {
            print("Main activity: " + _sharedText);

            Fluttertoast.showToast(msg: "shared: $_sharedText",
                toastLength: Toast.LENGTH_SHORT,
                gravity: ToastGravity.BOTTOM);



            showListOfCollections(context,false, _sharedText);
            //navigatorKey.currentState.pushNamed(CollectionListPage.routeName, arguments: Arguments(_sharedText,false,0,navigatorKey));

          }else{
            print("Main activity text: is null");
          }

          setState(() {
            _sharedText = null;
          });

        }, onError: (err) {
          Fluttertoast.showToast(msg: "getLinkStream error: $err",
              toastLength: Toast.LENGTH_SHORT,
              gravity: ToastGravity.BOTTOM);
          print("getLinkStream error: $err");
        });


    // For sharing or opening urls/text coming from outside the app while the app is closed
    ReceiveSharingIntent.getInitialText().then((String value) {
      setState(() {
        _sharedText = value;
        isSharing = true;
      });

      if (_sharedText != null) {
        print("Main activity app closed: " + _sharedText);

        Fluttertoast.showToast(msg: "Shared when closed: $_sharedText",
            toastLength: Toast.LENGTH_SHORT,
            gravity: ToastGravity.BOTTOM);

        showListOfCollections(context,false, _sharedText);
        //navigatorKey.currentState.pushNamed(CollectionListPage.routeName, arguments: Arguments(_sharedText,false,0,navigatorKey));
      }else{
        print("Main activity app closed text: is null");

      }

        setState(() {
          _sharedText = null;
        });
    });
  }

  void showListOfCollections(context,bool isImage,String sharingText){
    final context1 = navigatorKey.currentState.overlay.context;

    if (sharingText != "" && sharingText != null){
      print(sharingText);
      print("Showing dialog!");
      //final dialog = CollectionListPage(args: Arguments(sharingText,isImage,0,navigatorKey));
      final dialog = Dialog(
        backgroundColor: Colors.transparent,
        insetPadding: EdgeInsets.all(10),
        child: CollectionListPage(args: Arguments(sharingText,isImage,0,navigatorKey)),
      );
      showDialog(context: context1, builder: (x) => dialog);
    }


  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    if(state == AppLifecycleState.resumed){
      print("App resumed");

      Fluttertoast.showToast(msg: "App resumed",
          toastLength: Toast.LENGTH_SHORT,
          gravity: ToastGravity.BOTTOM);
    }else if(state == AppLifecycleState.inactive){
      print("App Inactive");
      Fluttertoast.showToast(msg: "App Inactive",
          toastLength: Toast.LENGTH_SHORT,
          gravity: ToastGravity.BOTTOM);
    }else if(state == AppLifecycleState.paused){
      print("App paused");
      Fluttertoast.showToast(msg: "App paused",
          toastLength: Toast.LENGTH_SHORT,
          gravity: ToastGravity.BOTTOM);
    }else if(state == AppLifecycleState.detached){
      print("App detached");
      Fluttertoast.showToast(msg: "App detached",
          toastLength: Toast.LENGTH_SHORT,
          gravity: ToastGravity.BOTTOM);
    }
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    _intentDataStreamSubscription.cancel();
    super.dispose();
  }

  Future<String> _calculation = Api().getMindUrl();

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      theme: ThemeData(primarySwatch: Colors.teal, accentColor: Color(0xFFDD5237)),
      home: Scaffold(
        appBar: AppBar(
          title:  const Text(Strings.title),
        ),
        body: FutureBuilder<String>(
          future: _calculation, // a previously-obtained Future<String> or null
          builder: (BuildContext context, AsyncSnapshot<String> snapshot) {
            List<Widget> children;
            if (snapshot.hasData) {
              print("Data: " + snapshot.data);
              /*Future.delayed(Duration(microseconds: 200)).then((value) {
                Tutorial.showTutorial(context, itens);
              });*/
              return _buildButtons(context,snapshot.data);
            } else if (snapshot.hasError) {
              children = <Widget>[
                Icon(
                  Icons.error_outline,
                  color: Colors.red,
                  size: 60,
                ),
                Padding(
                  padding: const EdgeInsets.only(top: 16),
                  child: Text('Error: ${snapshot.error}'),
                )
              ];
            } else {
              children = <Widget>[
                SizedBox(
                  child: CircularProgressIndicator(),
                  width: 60,
                  height: 60,
                ),
                const Padding(
                  padding: EdgeInsets.only(top: 16),
                  child: Text(Strings.waitText),
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
          },
        ),
        floatingActionButtonLocation: FloatingActionButtonLocation.centerFloat,
        floatingActionButton: _buildFab(
            context),
      ),
    );
  }

  Widget _buildFab(BuildContext context) {
    return new Container(
      padding: EdgeInsets.only(bottom: 5.0),
      child: Align(
        alignment: Alignment.bottomCenter,
        child: FloatingActionButton(
          key: keySettings,
          onPressed: () {
            Navigator.push(
              context,
              MaterialPageRoute(builder: (context) => settings()),
            );
          },
          tooltip: 'Settings',
          child: Icon(Icons.settings),
          focusColor: Colors.red,
          elevation: 3.0,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.all(Radius.circular(16.0))),
        ),

      ),
    );
  }

  Widget _buildButtons(BuildContext context,String url) {
    return new Scaffold(
      body: Padding(
        padding: const EdgeInsets.all(15.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.start,
          crossAxisAlignment: CrossAxisAlignment.center,
          children: [
            SizedBox(height: 30),
            Text('Welcome to your mind!',textAlign: TextAlign.center,
              overflow: TextOverflow.visible,
              style: TextStyle(fontWeight: FontWeight.bold,fontSize: 30)),
            SizedBox(height: 30),
            ElevatedButton.icon(
                key: keyOpenMindButton,
                icon: Icon(Icons.open_in_browser),
                label: Text(
                    Strings.openMindButton,
                  style: new TextStyle(fontSize: 20.0, color: Colors.white)),
                onPressed:() => Api().launchURL(url),
                style: ElevatedButton.styleFrom(
                  primary: Colors.teal,
                )
            ),
            SizedBox(
              height: 20,
            ),
            ElevatedButton.icon(
              key: keyOpenServerButton,
              icon: Icon(Icons.web),
              label: Text(
                  Strings.openServerButton,
                  style: new TextStyle(fontSize: 20.0, color: Colors.white)),
                onPressed:() => Api().launchSettings(),
                style: ElevatedButton.styleFrom(
                  primary: Colors.teal,
                ),
              ),
            SizedBox(
              height: 20,
            ),
            ElevatedButton.icon(
              key: keyRefreshCollections,
              icon: Icon(Icons.refresh),
              label: Text(
                  Strings.refreshCollectionButton,
                  style: new TextStyle(fontSize: 20.0, color: Colors.white)),
                onPressed:() => showDialog(context: context, builder: (x) => _buildRefreshNot()),
                style: ElevatedButton.styleFrom(
                  primary: Colors.teal,
                ),
            ),
            SizedBox(height: 30),
            Text(Strings.sloganBottom, textAlign: TextAlign.center,
                overflow: TextOverflow.visible,
                style: TextStyle(fontWeight: FontWeight.bold,fontSize: 20)),
            SizedBox(height: 25),
            ElevatedButton.icon(
              icon: Icon(Icons.feedback),
              label: Text(
                  Strings.openGithubRepo,
                  style: new TextStyle(fontSize: 20.0, color: Colors.white)),
              onPressed:() => Api().launchRepo(false),
              style: ElevatedButton.styleFrom(
                primary: Colors.teal,
              ),
            ),
            SizedBox(height: 25),
            ElevatedButton.icon(
              icon: Icon(Icons.report_problem),
              label: Text(
                  Strings.openGithubRepoIssue,
                  style: new TextStyle(fontSize: 20.0, color: Colors.white)),
              onPressed:() => Api().launchRepo(true),
              style: ElevatedButton.styleFrom(
                primary: Colors.teal,
              ),
            ),
          ],
        )
      ),
    );
  }

  Widget _buildRefreshNot() {
    return FutureBuilder<String>(
        future:  Api().refreshCollections(), // a previously-obtained Future<String> or null
        builder: (BuildContext context, AsyncSnapshot<String> snapshot) {
          List<Widget> children;
          if (snapshot.hasData) {
            final dialog = AlertDialog(
              // Retrieve the text the that user has entered by using the
              // TextEditingController.
              title: Text("Collections refreshed"),
              content: Text("Succesfully refreshed the collections"),
            );
            return dialog;
          } else if (snapshot.hasError) {
            final dialog = AlertDialog(
              // Retrieve the text the that user has entered by using the
              // TextEditingController.
              title: Text("Collections not refreshed"),
              content: Text('Error: ${snapshot.error}'),
            );
            return dialog;
          } else {
            children = <Widget>[
              SizedBox(
                child: CircularProgressIndicator(),
                width: 60,
                height: 60,
              ),
              const Padding(
                padding: EdgeInsets.only(top: 16),
                child: Text(Strings.waitText),
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
