package com.zenterio
/**
 * This code is taken from http://stackoverflow.com/a/37379139/209127
 * It is unclear what the license is.
 */

/**
 * HTML string utilities
 */
public class SafeHtml {

    /**
     * Escapes a string for use in an HTML entity or HTML attribute.
     *
     * <p>
     * The returned value is always suitable for an HTML <i>entity</i> but only
     * suitable for an HTML <i>attribute</i> if the attribute value is inside
     * double quotes. In other words the method is not safe for use with HTML
     * attributes unless you put the value in double quotes like this:
     * <pre>
     *    &lt;div title="value-from-this-method" &gt; ....
     * </pre>
     * Putting attribute values in double quotes is always a good idea anyway.
     *
     * <p>The following characters will be escaped:
     * <ul>
     *   <li>{@code &} (ampersand) -- replaced with {@code &amp;}</li>
     *   <li>{@code <} (less than) -- replaced with {@code &lt;}</li>
     *   <li>{@code >} (greater than) -- replaced with {@code &gt;}</li>
     *   <li>{@code "} (double quote) -- replaced with {@code &quot;}</li>
     *   <li>{@code '} (single quote) -- replaced with {@code &#39;}</li>
     *   <li>{@code /} (forward slash) -- replaced with {@code &#47;}</li>
     * </ul>
     * It is not necessary to escape more than this as long as the HTML page
     * <a href="https://en.wikipedia.org/wiki/Character_encodings_in_HTML">uses
     * a Unicode encoding</a>. (Most web pages uses UTF-8 which is also the HTML5
     * recommendation.). Escaping more than this makes the HTML much less readable.
     *
     * @param s the string to make HTML safe
     * @param avoidDoubleEscape avoid double escaping, which means for example not
     *     escaping {@code &lt;} one more time. Any sequence {@code &....;} as explained in
     *     {@link #isHtmlCharEntityRef(java.lang.String, int) isHtmlCharEntityRef()} will not be escaped.
     *
     * @return a HTML safe string
     */
    public static String htmlEscape(String s, boolean avoidDoubleEscape) {
        if (s == null || s.length() == 0) {
            return s;
        }
        StringBuilder sb = new StringBuilder(s.length()+16);
        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            switch (c) {
                case '&':
                    // Avoid double escaping if already escaped
                    if (avoidDoubleEscape && (isHtmlCharEntityRef(s, i))) {
                        sb.append('&');
                    } else {
                        sb.append("&amp;");
                    }
                    break;
                case '<':
                    sb.append("&lt;");
                    break;
                case '>':
                    sb.append("&gt;");
                    break;
                case '"':
                    sb.append("&quot;");
                    break;
                case '\'':
                    sb.append("&#39;");
                    break;
                case '/':
                    sb.append("&#47;");
                    break;
                default:
                    sb.append(c);
            }
        }
        return sb.toString();
  }

  /**
   * Checks if the value at {@code index} is a HTML entity reference. This
   * means any of :
   * <ul>
   *   <li>{@code &amp;} or {@code &lt;} or {@code &gt;} or {@code &quot;} </li>
   *   <li>A value of the form {@code &#dddd;} where {@code dddd} is a decimal value</li>
   *   <li>A value of the form {@code &#xhhhh;} where {@code hhhh} is a hexadecimal value</li>
   * </ul>
   * @param str the string to test for HTML entity reference.
   * @param index position of the {@code '&'} in {@code str}
   * @return
   */
  public static boolean isHtmlCharEntityRef(String str, int index)  {
      if (str.charAt(index) != '&') {
          return false;
      }
      int indexOfSemicolon = str.indexOf(';', index + 1);
      if (indexOfSemicolon == -1) { // is there a semicolon sometime later ?
          return false;
      }
      if (!(indexOfSemicolon > (index + 2))) {   // is the string actually long enough
          return false;
      }
      if (followingCharsAre(str, index, "amp;")
              || followingCharsAre(str, index, "lt;")
              || followingCharsAre(str, index, "gt;")
              || followingCharsAre(str, index, "quot;")) {
          return true;
      }
      if (str.charAt(index+1) == '#') {
          if (str.charAt(index+2) == 'x' || str.charAt(index+2) == 'X') {
              // It's presumably a hex value
              if (str.charAt(index+3) == ';') {
                  return false;
              }
              for (int i = index+3; i < indexOfSemicolon; i++) {
                  char c = str.charAt(i);
                  if (c >= 48 && c <=57) {  // 0 -- 9
                      continue;
                  }
                  if (c >= 65 && c <=70) {   // A -- F
                      continue;
                  }
                  if (c >= 97 && c <=102) {   // a -- f
                      continue;
                  }
                  return false;
              }
              return true;   // yes, the value is a hex string
          } else {
              // It's presumably a decimal value
              for (int i = index+2; i < indexOfSemicolon; i++) {
                  char c = str.charAt(i);
                  if (c >= 48 && c <=57) {  // 0 -- 9
                      continue;
                  }
                  return false;
              }
              return true; // yes, the value is decimal
          }
      }
      return false;
  }


  /**
   * Tests if the chars following position <code>startIndex</code> in string
   * <code>str</code> are that of <code>nextChars</code>.
   *
   * <p>Optimized for speed. Otherwise this method would be exactly equal to
   * {@code (str.indexOf(nextChars, startIndex+1) == (startIndex+1))}.
   *
   * @param str
   * @param startIndex
   * @param nextChars
   * @return
   */
  private static boolean followingCharsAre(String str, int startIndex, String nextChars)  {
      if ((startIndex + nextChars.length()) < str.length()) {
          for(int i = 0; i < nextChars.length(); i++) {
              if ( nextChars.charAt(i) != str.charAt(startIndex+i+1)) {
                  return false;
              }
          }
          return true;
      } else {
          return false;
      }
  }
}
