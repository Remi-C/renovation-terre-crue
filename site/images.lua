-- Filtre pandoc : réécrit le chemin des figures et des photos d'un sujet, quel que soit le chemin écrit dans le papier.
-- Une image dont le nom (sans extension) commence par « fig_ » pointe vers figures/<id>.svg sur le site et
-- figures/<id>.png dans le .docx (<id> garde son suffixe : fig_x_en pour la figure anglaise) ; une image de photos/ pointe vers photos/<nom>. Métadonnées lues :
--   prefixe_sujet  préfixe des liens du site vers le dossier du sujet (« » ou « ../../<sujet>/ ») ;
--   lien_references  adresse de la liste complète des sources dans le dépôt (pour `references.md` cité dans le texte).

local prefixe = ""
local lien_references = nil

local function nom_de(src)
  return src:match("([^/\\]+)$") or src
end

function Meta(m)
  if m.prefixe_sujet then prefixe = pandoc.utils.stringify(m.prefixe_sujet) end
  if m.lien_references then lien_references = pandoc.utils.stringify(m.lien_references) end
  return m
end

function Image(img)
  local nom = nom_de(img.src)
  local id = nom:gsub("%.[%w]+$", "")
  local html = FORMAT:match("html") ~= nil
  if id:match("^fig_") then
    if html then
      img.src = prefixe .. "figures/" .. id .. ".svg"
    else
      img.src = "figures/" .. id .. ".png"
      if not img.attributes.width then img.attributes.width = "16cm" end
    end
  elseif img.src:match("photos/") then
    img.src = (html and prefixe or "") .. "photos/" .. nom
    if not html and not img.attributes.width then img.attributes.width = "12cm" end
  end
  if html then img.attributes.loading = "lazy" end
  return img
end

-- Un lien vers `references.md` (ou `../references.md`) mène à la liste complète des sources, dans le dépôt GitHub
-- (le chemin relatif n'a de sens que sur GitHub) ; même chose pour le nom cité en code dans le texte.
function Link(l)
  if l.target:match("references%.md$") and lien_references then
    l.target = lien_references
  end
  return l
end

function Code(c)
  if c.text:match("references%.md$") and lien_references then
    return pandoc.Link({ pandoc.Code(c.text) }, lien_references)
  end
end

return { { Meta = Meta }, { Image = Image, Link = Link, Code = Code } }
