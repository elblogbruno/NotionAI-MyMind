import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

class Api {

  Future<String> getMindUrl() async {
    try {
      String _serverUrl = await getServerUrl();

      String serverUrl = _serverUrl + "get_current_mind_url";
      print("GetMindUrl: " + serverUrl);
      http.Response response = await http.get(serverUrl);

      if (response.statusCode == 200) {
        return response.body.toString();
      } else {
        return '-1';
      }
    } catch (_) {
      return '-1';
    }
  }

  Future<String> addUrlToMind(String urlToAdd,String title) async {
    try {
      String _serverUrl = await getServerUrl();
      String finalUrl = _serverUrl + "add_url_to_mind?url="+urlToAdd+"&title="+title;
      print("Final sharing url: " + finalUrl);
      http.Response response = await http.get(finalUrl);

      if (response.statusCode == 200) {
        return response.body.toString();
      } else {
        return '-1';
      }
    } catch (_) {
      return '-1';
    }
  }

  setServerUrl(String value) async {
    final SharedPreferences prefs = await SharedPreferences.getInstance();
    await prefs.setString("url", value);
  }


  Future<String> getServerUrl() async {
    final SharedPreferences prefs = await SharedPreferences.getInstance();
    return prefs.getString("url") ?? 'name';
  }
}