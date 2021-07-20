import 'dart:async';
import 'dart:convert';

import 'package:http/http.dart' as http;
import 'package:metadata_fetch/metadata_fetch.dart';
import 'package:notion_ai_my_mind/api/models/api_response.dart';
import 'package:notion_ai_my_mind/api/models/mind_collection.dart';
import 'package:notion_ai_my_mind/api/models/mind_collection_list_response.dart';
import 'package:notion_ai_my_mind/api/models/multi_select_tag_list_response.dart';
import 'package:notion_ai_my_mind/api/models/tag.dart';


import 'package:notion_ai_my_mind/resources/strings.dart';
import 'package:path/path.dart';
import 'package:async/async.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'dart:io';

import 'package:url_launcher/url_launcher.dart';
import 'package:notion_ai_my_mind/locales/main.i18n.dart';

class Api {
  static const int TIMEOUT_TIME = 5;

  //Gets mind structure
  Future<MindCollectionListResponse> getMindStructure() async {
    try {
      String _serverUrl = await getServerUrl();

      String finalUrl = _serverUrl + "get_mind_structure";

      Uri url = Uri.parse(finalUrl);
      print("Final get_mind_structure: " + url.toString());

      http.Response response = await http.get(url).timeout(
        Duration(seconds: TIMEOUT_TIME),
      );

      if (response.statusCode == 200) {
        Map map = jsonDecode(response.body);
        MindCollectionListResponse apiResponse = MindCollectionListResponse.fromJson(map);
        setCollections(response.body);
        return apiResponse;
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

  //Gets mind url asking to the server
  Future<String> getMindUrl() async {
    try {
      String _serverUrl = await getServerUrl();

      String finalUrl = _serverUrl + "get_current_mind_url";

      Uri url = Uri.parse(finalUrl);
      print("Final GetMindUrl: " + url.toString());

      http.Response response = await http.get(url).timeout(
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
    on ArgumentError  catch (_) {
      return Future.error(Strings.appNoConfigured.i18n);
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

            Uri url = Uri.parse(finalUrl);
            print("Final sharing url: " + url.toString());
            http.Response response = await http.get(url).timeout(
              Duration(seconds: TIMEOUT_TIME),
            );

            if (response.statusCode == 200) {
              return parseResponse(response.body);
            } else {
              return APIResponse.createBadResponse(Strings.badResultResponse.i18n);
            }
          }
          else if(urlToAdd == matches.first.group(0)) { //It is just an url, as the text and the url extracted from it are equal.
            final matchedText = matches.first.group(0);

            var data = await MetadataFetch.extract(matchedText);

            print("Web title: " + data.title); // my

            String title = matchedText + " added to your mind from Phone";

            if(data.title.isNotEmpty)
                title = data.title;

            String _serverUrl = await getServerUrl();
            String finalUrl = _serverUrl + "add_url_to_mind?collection_index="+collectionIndex.toString() + "&url=" + matchedText + "&title=" + title;

            Uri url = Uri.parse(finalUrl);
            print("Final sharing url: " + url.toString());
            http.Response response = await http.get(url).timeout(
              Duration(seconds: TIMEOUT_TIME),
            );

            if (response.statusCode == 200) {
              return  parseResponse(response.body);
            } else {
              return APIResponse.createBadResponse(Strings.badResultResponse.i18n);
            }
          }else{ //some text with urls on it
            final matchedText = matches.first.group(0);
            print("Match: " + matchedText); // my

            String _serverUrl = await getServerUrl();

            String finalUrl = _serverUrl + "add_text_to_mind?collection_index="+collectionIndex.toString() + "&url=" + matchedText + "&text=" + urlToAdd;

            Uri url = Uri.parse(finalUrl);
            print("Final sharing url: " + url.toString());
            http.Response response = await http.get(url).timeout(
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

      Uri url = Uri.parse(finalUrl);
      print("Final sharing url: " + url.toString());
      http.Response response = await http.get(url).timeout(
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

      Uri url = Uri.parse(finalUrl);
      print("Final setCollectionIndex url: " + url.toString());

      http.Response response = await http.get(url).timeout(
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

  Future<APIResponse> modifyElementById(String blockUrl,String newTitle,String newUrl) async {
    try {
      if(newTitle == null){
        newTitle = "";
      }

      if(newUrl == null){
        newUrl = "";
      }

      String _serverUrl = await getServerUrl();
      String finalUrl = _serverUrl + "modify_element_by_id?id=" + blockUrl+"&new_title="+newTitle+"&new_url="+newUrl;


      Uri url = Uri.parse(finalUrl);
      print("Final modify_element_by_id url: " + url.toString());

      http.Response response = await http.get(url).timeout(
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

  Future<APIResponse> setReminderDateToBlock(String blockUrl, String reminderStartDate,String unit,int remindValue, bool autoDestroy) async {
    try {
      String _serverUrl = await getServerUrl();
      String finalUrl = _serverUrl + "set_reminder_date_to_block?id="+blockUrl+"&start="+reminderStartDate+"&unit="+unit+"&remind_value="+remindValue.toString()+"&auto_destroy="+autoDestroy.toString();


      Uri url = Uri.parse(finalUrl);
      print("Final set_reminder_date_to_block url: " + url.toString());

      http.Response response = await http.get(url).timeout(
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

  Future<APIResponse> setMultiSelectTags(int collectionIndex,String blockId,List<dynamic> jsonList) async{
    try {
      String _serverUrl = await getServerUrl();
      String finalUrl = _serverUrl + "update_multi_select_tags";


      Uri url = Uri.parse(finalUrl);
      print("Final set_multi_select_tags url: " + url.toString());

      String jsonTags = jsonEncode(jsonList);
      print(jsonTags);
      final http.Response response = await http.post(
        url,
        headers: <String, String>{
          'Content-Type': 'application/json;  charset=UTF-8',
          'id': '${blockId}',
          'collection_index': '${collectionIndex}',
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

      Uri url = Uri.parse(finalUrl);
      print("Final get_multi_select_tags url: " + url.toString());

      http.Response response = await http.get(url).timeout(
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

  Future<APIResponse> addContentToMind(String url,bool isNotUrl,int index) async{
    print("addContentToMind: " + url + " " + isNotUrl.toString());
    if(url != null){
      print("Widget url: " + url);
      if(isNotUrl){
        print("Widget is an image, video or sound");
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

    m.multi_select_tag_list = [];
    //List<TAGResponse> collectionList = new List<TAGResponse>();

    for(int i = 0; i < data.length;i++){
      Map<String, dynamic> myMap = new Map<String, dynamic>.from(data[i]);
      Tag response = Tag.fromJson(myMap);
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

  Future<MindCollectionListResponse> getCollections() async {
    final SharedPreferences prefs = await SharedPreferences.getInstance();
    String structure = prefs.getString("structure") ?? null;
    return parseStructure(structure);
  }

  MindCollectionListResponse parseStructure(String responseBody) {
    if (responseBody != null) {
      Map map = jsonDecode(responseBody);

      MindCollectionListResponse resp = MindCollectionListResponse.fromJson(
          map);

      List<dynamic> data = resp.extra_content;

      resp.collections = new List<MindCollection>();

      for (int i = 0; i < data.length; i++) {
        //Map userMap = jsonDecode(data[i]);
        Map<String, dynamic> myMap = new Map<String, dynamic>.from(data[i]);
        var response = MindCollection.fromJson(myMap);
        resp.collections.add(response);
      }
      return resp;
    }
    else{
      return MindCollectionListResponse.createBadResponse(Strings.collectionsNotRefreshed.i18n);
    }
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