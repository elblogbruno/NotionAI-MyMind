import 'dart:convert';
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:fluttertoast/fluttertoast.dart';
import 'package:http/io_client.dart';
import 'package:notion_ai_my_mind/settings.dart';
import 'dart:async';

import 'package:receive_sharing_intent/receive_sharing_intent.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:webview_flutter/webview_flutter.dart';
import 'package:notion_ai_my_mind/api/api.dart';


void main() => runApp(MyApp());

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
        primarySwatch: Colors.blue,
        //primaryColor: Colors.red,
        //backgroundColor: Colors.white,
        //bottomAppBarColor: Colors.white,
      ),
      home: new MyHomePage(),
    );
  }
}

class MyHomePage extends StatefulWidget {
  @override
  _MyAppState createState() => _MyAppState();
}

class _MyAppState extends State<MyHomePage> with WidgetsBindingObserver {
  Future<SharedPreferences> _prefs = SharedPreferences.getInstance();
  final Completer<WebViewController> _controller =
  Completer<WebViewController>();
  StreamSubscription _intentDataStreamSubscription;
  List<SharedMediaFile> _sharedFiles;
  String _sharedText;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
    // For sharing images coming from outside the app while the app is in the memory
    _intentDataStreamSubscription = ReceiveSharingIntent.getMediaStream()
        .listen((List<SharedMediaFile> value) {
      setState(() {
        _sharedFiles = value;
        Fluttertoast.showToast(msg: "Shared:" + (_sharedFiles?.map((f) => f.path)?.join(",") ?? ""),
                  toastLength: Toast.LENGTH_SHORT,
                  gravity: ToastGravity.BOTTOM);

        print("Shared:" + (_sharedFiles?.map((f) => f.path)?.join(",") ?? ""));
      });
    }, onError: (err) {
      print("getIntentDataStream error: $err");
    });
  
    // For sharing images coming from outside the app while the app is closed
    ReceiveSharingIntent.getInitialMedia().then((List<SharedMediaFile> value) {
      setState(() {
        _sharedFiles = value;
        Fluttertoast.showToast(msg: "Shared:" + (_sharedFiles?.map((f) => f.path)?.join(",") ?? ""),
                          toastLength: Toast.LENGTH_SHORT,
                          gravity: ToastGravity.BOTTOM);

        print("Shared:" + (_sharedFiles?.map((f) => f.path)?.join(",") ?? ""));
      });
    });

    // For sharing or opening urls/text coming from outside the app while the app is in the memory
    _intentDataStreamSubscription =
        ReceiveSharingIntent.getTextStream().listen((String value) {
          setState(() {
            _sharedText = value;
            if(_sharedText != null) {
                Api().addUrlToMind(_sharedText, "Url from: $_sharedText");
                print("Shared: $_sharedText");

                Fluttertoast.showToast(msg: "Shared: $_sharedText",
                    toastLength: Toast.LENGTH_SHORT,
                    gravity: ToastGravity.BOTTOM);
            }else{
                print("Shared text is null");
            }
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

        if(_sharedText != null) {
            Api().addUrlToMind(_sharedText, "Url from: $_sharedText");
            print("Shared: $_sharedText");

            Fluttertoast.showToast(msg: "Shared when app closed: $_sharedText",
                toastLength: Toast.LENGTH_SHORT,
                gravity: ToastGravity.BOTTOM);
        }else{
          print("Shared text is null");
        }

      });
    });
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
    const textStyleBold = const TextStyle(fontWeight: FontWeight.bold);
    return MaterialApp(
      home: Scaffold(
        appBar: AppBar(
          title:  const Text("Notion AI My Mind"),
        ),
        body: FutureBuilder<String>(
          future: _calculation, // a previously-obtained Future<String> or null
          builder: (BuildContext context, AsyncSnapshot<String> snapshot) {
            List<Widget> children;
            if (snapshot.hasData) {
              return _BuildWebView(context,snapshot.data);
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
                  child: Text('Awaiting result...'),
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
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (context) => settings()),
              );
            },
            tooltip: 'Increment',
            child: Icon(Icons.settings),
            focusColor: Colors.red,
            elevation: 3.0,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.all(Radius.circular(16.0))),
          ),

        ),
      );
    }

    Widget _BuildWebView(BuildContext context,String url){
      return new WebView(
        initialUrl: url,
        javascriptMode: JavascriptMode.unrestricted,
        onWebViewCreated: (WebViewController webViewController) {
          _controller.complete(webViewController);
        },
        // TODO(iskakaushik): Remove this when collection literals makes it to stable.
        // ignore: prefer_collection_literals
        javascriptChannels: <JavascriptChannel>[
          _toasterJavascriptChannel(context),
        ].toSet(),
        navigationDelegate: (NavigationRequest request) {
          if (request.url.startsWith('https://www.youtube.com/')) {
            print('blocking navigation to $request}');
            return NavigationDecision.prevent;
          }
          print('allowing navigation to $request');
          return NavigationDecision.navigate;
        },
        onPageStarted: (String url) {
          print('Page started loading: $url');
        },
        onPageFinished: (String url) {
          print('Page finished loading: $url');
        },
        gestureNavigationEnabled: true,
      );
    }
  JavascriptChannel _toasterJavascriptChannel(BuildContext context) {
    return JavascriptChannel(
        name: 'Toaster',
        onMessageReceived: (JavascriptMessage message) {
          Scaffold.of(context).showSnackBar(
            SnackBar(content: Text(message.message)),
          );
        });
  }

}
