class Response {
  final int status_code;
  final String text_response;
  final String status_text;
  final String block_url;

  Response({this.status_code, this.text_response, this.status_text,this.block_url});

  factory Response.fromJson(Map<String, dynamic> json) {
    return Response(
      status_code: json['status_code'] as int,
      text_response: json['text_response'] as String,
      status_text: json['status_text'] as String,
      block_url: json['block_url'] as String,
    );
  }
}