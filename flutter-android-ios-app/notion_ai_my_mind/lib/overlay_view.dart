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


class OverlayView extends StatefulWidget {
  @override
  _MyAppState createState() => _MyAppState();
}

class _MyAppState extends State<OverlayView> {
  StreamSubscription _intentDataStreamSubscription;
  List<SharedMediaFile> _sharedFiles;
  String _sharedText;

  @override
  void initState() {
    super.initState();
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
              Api().addUrlToMind(_sharedText);
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
          Api().addUrlToMind(_sharedText);
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
  void dispose() {
    _intentDataStreamSubscription.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    // TODO: implement build
    throw UnimplementedError();
  }


}
