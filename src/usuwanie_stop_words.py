""" usuwanie stop words """
import spacy

nlp = spacy.load("en_core_web_sm")


def remove_stop_words(text: str) -> str:
    doc = nlp(text)
    # co ze spacjami między tokenami?
    text_parts = [token.text for token in doc if not token.is_stop]
    return "".join(text_parts)


# Similar to semantic segmentation of images, videos, and scenes, text can be
# segmented based on meaning. This is a better bucketing technique for vectors
# because chunks will have sufficiently different meanings and hence
# significantly different vectors. We can use spaCy to vectorize sentences
# (using word2vec under the hood), and then group sentences together if their
# similarity falls above a threshold. We’ll use a value of 0.8, which is the
# result of taking the dot product of two vectors and then dividing it by the
# product of the vectors’ norms.

nlp = spacy.load("en_core_web_sm")


def split_sentences(text: str) -> list:
    doc = nlp(text)
    sentences = [sent.text for sent in doc.sents]
    return sentences


def group_sentences_semantically(sentences: list, threshold: int) -> list:
    """ grupowanie zdań według znaczenia/tematu"""
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


def split_text(text: str) -> list:
    text_no_stop_words = remove_stop_words(text)
    sentences = split_sentences(text_no_stop_words)
    return group_sentences_semantically(sentences, 0.8)
