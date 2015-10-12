% include("header.tpl", title="Viper Web Interface")
<div>
                <div>
                    <form role="form" action="/decode" enctype="multipart/form-data" method="post">
                        <div class="form-group">
                            <textarea class="form-control" rows="20" name="encoded_data">{{decoded}}</textarea>
                        </div>
                        
                          <div class="form-group form-inline">
                              <select class="form-control" name="return_type">
                                <option value="form">Form</option>
                                <option value="file">File</option>
                            </select>
                             | <button type="submit" class="btn btn-info" name="decode_as" value="hex_d">HEX Decode</button>
                            <button type="submit" class="btn btn-info" name="decode_as" value="hex_e">HEX Encode</button> | 
                            <button type="submit" class="btn btn-info" name="decode_as" value="base64_d">B64 Decode</button>
                            <button type="submit" class="btn btn-info" name="decode_as" value="base64_e">B64 Encode</button>
                          </div>
                        
                        
                    </form>
                </div>
</div>
% include("footer.tpl")
