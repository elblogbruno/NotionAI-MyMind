import 'package:flutter/material.dart';

class Arguments{
  final String url;
  final bool isImage;
  int collection_index;
  final GlobalKey<NavigatorState> navigatorKey;
  Arguments(this.url,this.isImage,this.collection_index,this.navigatorKey);
}