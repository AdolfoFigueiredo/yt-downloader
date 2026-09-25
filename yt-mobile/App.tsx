import React, { useCallback, useState } from "react";
import { ActivityIndicator, Alert, Pressable, ScrollView, StyleSheet, Text, TextInput, View } from "react-native";
import * as Clipboard from "expo-clipboard";
import { StatusBar } from "expo-status-bar";
import { checkHealth, requestDownload, type MediaType, type Platform, type PlaylistKind } from "./src/api";
import { colors } from "./src/theme";
import SegmentedOption from "./src/components/SegmentedOption";

export default function App() {
  const [url, setUrl] = useState("");
  const [platform, setPlatform] = useState<Platform>("youtube");
  const [media, setMedia] = useState<MediaType>("video");
  const [kind, setKind] = useState<PlaylistKind>("single");
  const [loading, setLoading] = useState(false);
  const [feedback, setFeedback] = useState<string | null>(null);

  const paste = useCallback(async () => {
    const text = await Clipboard.getStringAsync();
    if (text) setUrl(text.trim());
  }, []);

  const download = useCallback(async () => {
    if (!url.trim()) {
      Alert.alert("Atencao", "Cole o link do video ou playlist.");
      return;
    }
    setLoading(true);
    setFeedback(null);
    try {
      const online = await checkHealth();
      if (!online) throw new Error("API fora do ar. Confira EXPO_PUBLIC_API_URL.");
      const r = await requestDownload(platform, media, kind, {
        url: url.trim(),
      });
      const dest = r.destiny ?? r.destino ?? "";
      setFeedback(`OK: ${r.message ?? r.mensagem ?? "Concluido!"}${dest ? `\n${dest}` : ""}`);
    } catch (e) {
      setFeedback(`Erro: ${e instanceof Error ? e.message : String(e)}`);
    } finally {
      setLoading(false);
    }
  }, [url, platform, media, kind]);

  return (
    <View style={s.container}>
      <StatusBar style="light" />
      <ScrollView contentContainerStyle={s.scroll}>
        <Text style={s.logo}>AV-Downloader</Text>
        <Text style={s.title}>Baixar</Text>
        <Text style={s.sub}>Vídeos, áudios e playlists do YouTube</Text>
        <Text style={s.label}>Link</Text>
        <TextInput style={s.input} placeholder="https://..." placeholderTextColor={colors.grayDark} value={url} onChangeText={setUrl} autoCapitalize="none" autoCorrect={false} keyboardType="url" />
        <Pressable onPress={paste}><Text style={s.link}>Colar da area de transferencia</Text></Pressable>
        <Text style={s.label}>Plataforma</Text>
        <View style={s.row}>
          <SegmentedOption label="YouTube" selected={platform === "youtube"} onPress={() => setPlatform("youtube")} />
          <SegmentedOption label="X / Twitter" selected={platform === "x"} onPress={() => { setPlatform("x"); setKind("single"); }} />
        </View>
        <Text style={s.label}>Formato</Text>
        <View style={s.row}>
          <SegmentedOption label="MP4 Video" selected={media === "video"} onPress={() => setMedia("video")} />
          <SegmentedOption label="MP3 Audio" selected={media === "audio"} onPress={() => setMedia("audio")} />
        </View>
        {platform === "youtube" && (
          <View>
            <Text style={s.label}>Tipo</Text>
            <View style={s.row}>
              <SegmentedOption label="Unico" selected={kind === "single"} onPress={() => setKind("single")} />
              <SegmentedOption label="Playlist" selected={kind === "playlist"} onPress={() => setKind("playlist")} />
            </View>
          </View>
        )}
        <Text style={s.defaultHint}>Os arquivos são salvos na pasta padrão configurada na API.</Text>
        <Pressable style={[s.cta, loading && s.off]} onPress={download} disabled={loading}>
          {loading ? <ActivityIndicator color={colors.white} /> : <Text style={s.ctaTx}>Baixar {media === "video" ? "MP4" : "MP3"}</Text>}
        </Pressable>
        {feedback && <Text style={s.fb}>{feedback}</Text>}
        <Text style={s.hint}>Emulador: http://10.0.2.2:8000. Celular: IP da maquina via EXPO_PUBLIC_API_URL.</Text>
      </ScrollView>
    </View>
  );
}

const s = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  scroll: { padding: 20, paddingTop: 60, gap: 8 },
  logo: { color: colors.primary, fontWeight: "800", fontSize: 16 },
  title: { color: colors.white, fontSize: 26, fontWeight: "800" },
  sub: { color: colors.gray, marginBottom: 10 },
  label: { color: colors.grayLight, fontWeight: "700", marginTop: 12 },
  input: { backgroundColor: colors.graphite, borderColor: colors.border, borderWidth: 1, borderRadius: 10, padding: 12, color: colors.white, marginTop: 6 },
  link: { color: colors.blue, marginTop: 8 },
  row: { flexDirection: "row", gap: 8, marginTop: 6 },
  cta: { marginTop: 20, backgroundColor: colors.primary, borderRadius: 26, paddingVertical: 15, alignItems: "center" },
  off: { opacity: 0.6 },
  ctaTx: { color: colors.white, fontWeight: "800", fontSize: 16 },
  fb: { marginTop: 14, backgroundColor: colors.graphiteLight, color: colors.white, padding: 12, borderRadius: 10 },
  hint: { color: colors.grayDark, marginTop: 14, fontSize: 12 },
  defaultHint: { color: colors.gray, fontSize: 12, marginTop: 16 },
});
