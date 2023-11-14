""" semantic segmentation """
import spacy


nlp = spacy.load("pl_core_news_lg")

def remove_stop_words(text: str) -> str:
  doc = nlp(text)
  text_parts = [token.text for token in doc if not token.is_stop]
  return "".join(text_parts)

def split_sentences(text: str) -> List[str]:
  doc = nlp(text)
  sentences = [sent.text for sent in doc.sents]
  return sentences

def group_sentences_semantically(sentences: List[str], threshold: int) -> List[str]:
  docs = [nlp(sentence) for sentence in sentences]
  segments = []

  start_idx = 0
  end_idx = 1
  segment = [sentences[start_idx]]
  while end_idx < len(docs):
    if docs[start_idx].similarity(docs[end_idx]) >= threshold:
      segment.append(docs[end_idx])
    else:
      segments.append(" ".join(segment))
      start_idx = end_idx
      segment = [sentences[start_idx]]
    end_idx += 1

  if segment:
    segments.append(" ".join(segment))

  return segments

def split_text(text: str) -> List[str]:
  text_no_stop_words = remove_stop_words(text)
  sentences = split_sentences(text_no_stop_words)
  return group_sentences_semantically(sentences, 0.8)