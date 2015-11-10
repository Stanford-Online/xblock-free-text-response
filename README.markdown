# FreeText XBlock
XBlock to capture a free-text response.

This package provides an XBlock for use with the EdX Platform and makes
it possible for instructors to creqte questions that expect a
free-text response.

Instructors define the following paramters in Studio:
- display name
- display correctness (True/False)
- Full-Credit Phrases
- Half-Credit Phrases
- Maximum Number of Attempts
- Maximum Word Count
- Minimum Word Count
- Prompt
- Question Weight

Students enter and submit their free-text responses, which instantly gets evaluated
according to the parameters above.

# Installation
- Add the xblock to your requirements/edx/github.text file
  e.g. -e git+https://github.com/Stanford-Online/xblock-free-text-response@cfb793db182b60281875b83b53a98640d740ebcf#egg=xblock-free-text-response

- In Studio Settings/Advanced Settings add the xblock to the Advanced Module List.
  e.g. "freetextresponse"

Now, when you create a component "Free-text Response" should appear in the Advanced Component List.
