class APIResponse {
  final int status_code;
  final String text_response;
  final String status_text;
  final String block_url;
  final String block_title;
  final String block_attached_url;

  APIResponse({this.status_code, this.text_response, this.status_text,this.block_url,this.block_title,this.block_attached_url});

  factory APIResponse.fromJson(Map<String, dynamic> json) {
    return APIResponse(
      status_code: json['status_code'] as int,
      text_response: json['text_response'] as String,
      status_text: json['status_text'] as String,
      block_url: json['block_url'] as String,
      block_title: json['block_title'] as String,
      block_attached_url: json['block_attached_url'] as String,
    );
  }
}