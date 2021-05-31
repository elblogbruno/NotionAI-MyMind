import 'dart:async';
import 'dart:convert';

import 'package:http/http.dart' as http;
import 'package:notion_ai_my_mind/api/models/mind_collection_list_response.dart';
import 'package:notion_ai_my_mind/api/models/multi_select_tag_list_response.dart';


import 'package:notion_ai_my_mind/resources/strings.dart';
import 'package:path/path.dart';
import 'package:async/async.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'dart:io';

import 'package:url_launcher/url_launcher.dart';

import 'models/mind_collection.dart';
import 'models/api_response.dart';
import 'models/tag.dart';

import 'package:notion_ai_my_mind/locales/main.i18n.dart';

class Api {
  static const int TIMEOUT_TIME = 5;
  Future<MindCollectionListResponse> refreshCollections() async {
    try {
      String _serverUrl = await getServerUrl();

      String serverUrl = _serverUrl + "get_mind_structure";
      print("get_mind_structure: " + serverUrl);
      http.Response response = await http.get(serverUrl).timeout(
        Duration(seconds: TIMEOUT_TIME),
      );

      if (response.statusCode == 200) {
        Map map = jsonDecode(response.body);
        MindCollectionListResponse api_response = MindCollectionListResponse.fromJson(map);
        setCollections(response.body);
        return api_response;
      } else {
        return Future.error(Strings.serverTimeout.i18n.i18n);
      }
    }
    on TimeoutException catch (_) {
      return Future.error(Strings.serverTimeout.i18n.i18n);
    }
    on SocketException catch (_) {
      return Future.error(Strings.noInternet.i18n.i18n);
    }
  }
  Future<String> getMindUrl() async {
    try {
      String _serverUrl = await getServerUrl();

      String serverUrl = _serverUrl + "get_current_mind_url";
      print("GetMindUrl: " + serverUrl);
      http.Response response = await http.get(serverUrl).timeout(
        Duration(seconds: TIMEOUT_TIME),
      );

      print(response.statusCode);
      if (response.statusCode == 200) {
        return response.body.toString();
      } else {
        return Future.error(Strings.serverTimeout.i18n);
      }
    }
    on TimeoutException catch (_) {
      return Future.error(Strings.serverTimeout.i18n);
    }
    on SocketException catch (_) {
      return Future.error(Strings.noInternet.i18n);
    }
  }

  Future<APIResponse> addUrlToMind(String urlToAdd,int collectionIndex) async {
    try {
      RegExp exp = new RegExp(r'(?:(?:https?|ftp):\/\/)?[\w/\-?=%.]+\.[\w/\-?=%.]+');
      Iterable<RegExpMatch> matches = exp.allMatches(urlToAdd);

      print("Matches lenght " + matches.length.toString());
      if (matches == null) {

      } else {
          if(matches.length == 0) //means no url extracted on the text. it is just text.
          {
            String title = "Extract from unknown url added to your mind from Phone";
            String _serverUrl = await getServerUrl();
            String finalUrl = _serverUrl + "add_text_to_mind?collection_index="+collectionIndex.toString() + "&url=" + title + "&text=" + urlToAdd;
            print("Final sharing url: " + finalUrl);
            http.Response response = await http.get(finalUrl).timeout(
              Duration(seconds: TIMEOUT_TIME),
            );

            if (response.statusCode == 200) {
              return parseResponse(response.body);
            } else {
              return APIResponse.createBadResponse(Strings.badResultResponse.i18n);
            }
          }
          else if(urlToAdd == matches.first.group(0)) { //It is just an url, as the text and the url extracted from it are equal.
            print(matches.first.group(0));

            final matchedText = matches.first.group(0);
            print("Match: " + matchedText); // my

            String title = matchedText + " added to your mind from Phone";
            String _serverUrl = await getServerUrl();
            String finalUrl = _serverUrl + "add_url_to_mind?collection_index="+collectionIndex.toString() + "&url=" + matchedText + "&title=" + title;
            print("Final sharing url: " + finalUrl);
            http.Response response = await http.get(finalUrl).timeout(
              Duration(seconds: TIMEOUT_TIME),
            );

            if (response.statusCode == 200) {
              return  parseResponse(response.body);
            } else {
              return APIResponse.createBadResponse(Strings.badResultResponse.i18n);
            }
          }else{
            print(matches.first.group(0));

            final matchedText = matches.first.group(0);
            print("Match: " + matchedText); // my

            String _serverUrl = await getServerUrl();
            String finalUrl = _serverUrl + "add_text_to_mind?collection_index="+collectionIndex.toString() + "&url=" + matchedText + "&text=" + urlToAdd;

            print("Final sharing url: " + finalUrl);
            http.Response response = await http.get(finalUrl).timeout(
              Duration(seconds: TIMEOUT_TIME),
            );

            if (response.statusCode == 200) {
              return  parseResponse(response.body);
            } else {
              return APIResponse.createBadResponse(Strings.badResultResponse.i18n);
            }
          }

      }

    } on TimeoutException catch (e) {
      print(e.toString());
      return Future.error(APIResponse.createBadResponse(Strings.serverTimeout.i18n));
    }
    on SocketException catch (e) {
      print(e.toString());
      return Future.error(APIResponse.createBadResponse(Strings.noInternet.i18n));
    }
  }

  Future<String> addImageToMind(String urlToAdd) async {
    try {

      String title = urlToAdd + " added to your mind from Phone";
      String _serverUrl = await getServerUrl();
      String finalUrl = _serverUrl + "add_image_to_mind?url="+urlToAdd+"&image_src="+title+"&image_src_url="+title;

      print("Final sharing url: " + finalUrl);

      http.Response response = await http.get(finalUrl).timeout(
        Duration(seconds: TIMEOUT_TIME),
      );

      if (response.statusCode == 200) {
        return "200";
      } else {
        return '-1';
      }
    } catch (_) {
      return '-1';
    }
  }

  Future<String> setCollectionIndex(int index) async {
    try {

      String _serverUrl = await getServerUrl();
      String finalUrl = _serverUrl + "set_collection_index?collection_index="+index.toString();

      print("Final setCollectionIndex url: " + finalUrl);

      http.Response response = await http.get(finalUrl).timeout(
        Duration(seconds: TIMEOUT_TIME),
      );

      if (response.statusCode == 200) {
        return "200";
      } else {
        return '-1';
      }
    } on TimeoutException catch (_) {
      return Future.error(Strings.serverTimeout.i18n);
    }
    on SocketException catch (_) {
      return Future.error(Strings.noInternet.i18n);
    }
  }

  Future<APIResponse> modify_element_by_id(String url,String newTitle,String newUrl,APIResponse block) async {
    try {
      if(newTitle == null){
        newTitle = "";
      }

      if(newUrl == null){
        newUrl = "";
      }

      String _serverUrl = await getServerUrl();
      String finalUrl = _serverUrl + "modify_element_by_id?id=" + url+"&new_title="+newTitle+"&new_url="+newUrl;

      print("Final modify_element_by_id url: " + finalUrl);

      http.Response response = await http.get(finalUrl).timeout(
        Duration(seconds: TIMEOUT_TIME),
      );

      if (response.statusCode == 200) {
        return  parseResponse(response.body);
      } else {
        return APIResponse.createBadResponse(Strings.badResultResponse.i18n);
      }
    } on TimeoutException catch (e) {
      return Future.error(APIResponse.createBadResponse(Strings.serverTimeout.i18n));
    }
    on SocketException catch (e) {
      return Future.error(APIResponse.createBadResponse(Strings.noInternet.i18n));
    }
  }

  Future<APIResponse> uploadImage(File imageFile,int index) async {
    try {
      //setCollectionIndex(index);

      var stream = new http.ByteStream(
          DelegatingStream.typed(imageFile.openRead()));
      var length = await imageFile.length();

      String _serverUrl = await getServerUrl();
      String uploadURL = _serverUrl + "upload_file";
      print("Final upload url: " + uploadURL);

      var uri = Uri.parse(uploadURL);
      var request = new http.MultipartRequest("POST", uri);

      Map<String, String> requestHeaders = {
        'collection_index': index.toString(),
      };
      request.headers.addAll(requestHeaders);
      var multipartFile = new http.MultipartFile('file', stream, length,
          filename: basename(imageFile.path));
      //contentType: new MediaType('image', 'png'));

      request.files.add(multipartFile);

      var response = await request.send().timeout(
        Duration(seconds: TIMEOUT_TIME),
      );
      print(response.statusCode);

      var response1 = await http.Response.fromStream(response);

      if (response.statusCode == 200) {
        return parseResponse(response1.body);
      } else {
        return APIResponse.createBadResponse(Strings.badResultResponse.i18n);
      }
    }
    on TimeoutException catch (e) {
      return Future.error(APIResponse.createBadResponse(Strings.serverTimeout.i18n));
    }
    on SocketException catch (e) {
      return Future.error(APIResponse.createBadResponse(Strings.noInternet.i18n));
    }
  }

  Future<APIResponse> set_multi_select_tags(int collection_index,String block_id,List<dynamic> jsonList) async{
    try {
      String _serverUrl = await getServerUrl();
      String finalUrl = _serverUrl + "update_multi_select_tags";

      print("Final set_multi_select_tags url: " + finalUrl);
      /*String jsonTags = "";
      for(int i = 0; i < jsonList.length;i++){
        jsonTags = jsonTags + "," + jsonList[i].toJson();
        print(jsonTags);
      }*/
      String jsonTags = jsonEncode(jsonList);
      print(jsonTags);
      final http.Response response = await http.post(
        finalUrl,
        headers: <String, String>{
          'Content-Type': 'application/json;  charset=UTF-8',
          'id': '${block_id}',
          'collection_index': '${collection_index}',
        },

        body: jsonTags,
      ).timeout(
        Duration(seconds: TIMEOUT_TIME),
      );

      if (response.statusCode == 200) {
        return  parseResponse(response.body);
      } else {
        return Future.error(APIResponse.createBadResponse(response.statusCode.toString()));
      }
    } on TimeoutException catch (e) {
      return Future.error(APIResponse.createBadResponse(Strings.serverTimeout.i18n));
    }
    on SocketException catch (e) {
      return Future.error(APIResponse.createBadResponse(Strings.noInternet.i18n));
    }
  }

  Future<MultiSelectTagListResponse> get_multi_select_tags(int collectionIndex) async{
    try {
      String _serverUrl = await getServerUrl();
      String finalUrl = _serverUrl + "get_multi_select_tags?collection_index="+collectionIndex.toString();

      print("Final get_multi_select_tags url: " + finalUrl);

      http.Response response = await http.get(finalUrl).timeout(
        Duration(seconds: TIMEOUT_TIME),
      );

      if (response.statusCode == 200) {
        return  parseMultiSelectResponse(response.body);
      } else {
        return  MultiSelectTagListResponse.createBadResponse(Strings.badResultResponse.i18n);
      }
    } on TimeoutException catch (e) {
      return Future.error(MultiSelectTagListResponse.createBadResponse(Strings.serverTimeout.i18n));
    }
    on SocketException catch (e) {
      return Future.error(MultiSelectTagListResponse.createBadResponse(Strings.noInternet.i18n));
    }
  }

  Future<List<String>> get_multi_select_tags_as_string(int collectionIndex) async{
    try {
      String _serverUrl = await getServerUrl();
      String finalUrl = _serverUrl + "get_multi_select_tags?collection_index="+collectionIndex.toString();

      print("Final get_multi_select_tags url: " + finalUrl);

      http.Response response = await http.get(finalUrl).timeout(
        Duration(seconds: TIMEOUT_TIME),
      );

      if (response.statusCode == 200) {
        Map map = jsonDecode(response.body);
        List<String> data = map["multi_select_tag_list"];
        print(data);
        return  data;
      } else {
        List<String> data = new List<String>();
        return  data;
      }
    } on TimeoutException catch (e) {
      return Future.error(APIResponse.createBadResponse(Strings.serverTimeout.i18n));
    }
    on SocketException catch (e) {
      return Future.error(APIResponse.createBadResponse(Strings.noInternet.i18n));
    }
  }

  Future<APIResponse> addContentToMind(String url,bool isImage,int index) async{
    print("addContentToMind: " + url + " " + isImage.toString());
    if(url != null){
      print("Widget url: " + url);
      if(isImage){
        print("Widget is image");
        var myFile = new File(url);
        return uploadImage(myFile,index);
      }else{
        print("Widget is url");
        return addUrlToMind(url,index);
      }
    }else{
      return APIResponse.createBadResponse(Strings.badResultResponse.i18n);
    }
  }

  APIResponse parseResponse(String responseBody) {
    Map userMap = jsonDecode(responseBody);
    var response = APIResponse.fromJson(userMap);
    return response;
  }

  MultiSelectTagListResponse parseMultiSelectResponse(String responseBody) {
    Map map = jsonDecode(responseBody);

    MultiSelectTagListResponse m = MultiSelectTagListResponse.fromJson(map);

    List<dynamic> data = m.extra_content;

    m.multi_select_tag_list = new List<Tag>();
    //List<TAGResponse> collectionList = new List<TAGResponse>();

    for(int i = 0; i < data.length;i++){
      Map<String, dynamic> myMap = new Map<String, dynamic>.from(data[i]);
      var response = Tag.fromJson(myMap);
      m.multi_select_tag_list.add(response);
    }

    return m;
  }

  List<Tag> createBadTagResponse() {
    List<Tag> collectionList = new List<Tag>();
    Tag tag = Tag(
      option_color: "-1",
      option_id: "-1",
      option_name: "-1"
    );
    collectionList.add(tag);
    return collectionList;
  }

  /*Collection API*/

  setCollections(String value) async {
    final SharedPreferences prefs = await SharedPreferences.getInstance();

    await prefs.setString("structure", value);
  }

  Future<List<MindCollection>> getCollections() async {
    final SharedPreferences prefs = await SharedPreferences.getInstance();
    String structure = prefs.getString("structure") ?? null;
    return parseStructure(structure);
  }

  List<MindCollection> parseStructure(String responseBody) {
    Map map = jsonDecode(responseBody);

    MindCollectionListResponse resp = MindCollectionListResponse.fromJson(map);

    List<dynamic> data = resp.extra_content;

    resp.collections = new List<MindCollection>();

    for(int i = 0; i < data.length;i++){
      //Map userMap = jsonDecode(data[i]);
      Map<String, dynamic> myMap = new Map<String, dynamic>.from(data[i]);
      var response = MindCollection.fromJson(myMap);
      resp.collections.add(response);
    }
    return  resp.collections;
  }

  /*Server API*/

  setServerUrl(String value) async {
    final SharedPreferences prefs = await SharedPreferences.getInstance();

    if (value[value.length-1] != "/"){
      value = value + "/";
    }

    await prefs.setString("url", value);
  }

  Future<String> getServerUrl() async {
    final SharedPreferences prefs = await SharedPreferences.getInstance();
    return prefs.getString("url") ?? 'name';
  }

  launchSettings() async {
    String _serverUrl = await getServerUrl();
    launchURL(_serverUrl);
  }
  launchRepo(bool issues) async {
    if (issues)
      launchURL("https://github.com/elblogbruno/NotionAI-MyMind/issues");
    else
      launchURL("https://github.com/elblogbruno/NotionAI-MyMind");
  }

  launchURL(String url) async {
    if (await canLaunch(url)) {
      await launch(url);
    } else {
      throw 'Could not launch $url';
    }
  }
}