import 'package:flutter/material.dart';

class Arguments{
  final String url;
  final bool isNotUrl;
  int collection_index;
  final GlobalKey<NavigatorState> navigatorKey;
  Arguments(this.url,this.isNotUrl,this.collection_index,this.navigatorKey);
}